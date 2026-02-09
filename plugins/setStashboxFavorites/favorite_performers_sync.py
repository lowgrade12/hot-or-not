import math
import sys
import json
import ssl
import urllib.request
import urllib.error
import log

# Create SSL context that doesn't verify certificates (for self-signed certs)
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

def stashbox_call_graphql(endpoint, boxapi_key, query, variables=None):
    """Make a GraphQL request to a stash-box endpoint using standard library."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "ApiKey": boxapi_key
    }
    
    data = json.dumps({
        "query": query,
        "variables": variables or {}
    }).encode("utf-8")
    
    req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("errors"):
                for error in result["errors"]:
                    log.error("GraphQL error: {}".format(error.get("message", error)))
            return result.get("data")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            log.error("[ERROR][GraphQL] HTTP Error 401, Unauthorised. You need to add a Stash box instance and API Key in your Stash config")
        else:
            log.error(f"GraphQL query failed: {e.code} - {e.reason}")
        return None
    except urllib.error.URLError as e:
        log.error(f"Connection error: {e.reason}")
        return None
    except Exception as err:
        log.error(str(err))
        return None

def get_stashbox_performer_favorite(endpoint, boxapi_key, stash_id):
    query = """
query FullPerformer($id: ID!) {
  findPerformer(id: $id) {
    id
    is_favorite
  }
}
    """

    variables = {
        "id": stash_id
    }

    return stashbox_call_graphql(endpoint, boxapi_key, query, variables)

def update_stashbox_performer_favorite(endpoint: str, boxapi_key: str, stash_id: str, favorite: bool):
    query = """
mutation FavoritePerformer($id: ID!, $favorite: Boolean!) {
  favoritePerformer(id: $id, favorite: $favorite)
}
"""

    variables = {
        "id": stash_id,
        "favorite": favorite
    }

    return stashbox_call_graphql(endpoint, boxapi_key, query, variables)

def get_favorite_performers_from_stashbox(endpoint: str, boxapi_key: str):
    query = """
query Performers($input: PerformerQueryInput!) {
  queryPerformers(input: $input) {
    count
    performers {
      id
      is_favorite
    }
  }
}
"""

    per_page = 100

    variables = {
        "input": {
            "names": "",
            "is_favorite": True,
            "page": 1,
            "per_page": per_page,
            "sort": "NAME",
            "direction": "ASC"
        }
    }

    performers = set()

    total_count = None
    request_count = 0
    max_request_count = 1

    performercounts = {}

    while request_count < max_request_count:
        result = stashbox_call_graphql(endpoint, boxapi_key, query, variables)
        request_count += 1
        variables["input"]["page"] += 1
        if not result:
            break
        query_performers = result.get("queryPerformers")
        if not query_performers:
            break
        if total_count is None:
            total_count = query_performers.get("count")
            max_request_count = math.ceil(total_count / per_page)

        log.info(f'Received page {variables["input"]["page"] - 1} of {max_request_count}')
        log.progress(((variables["input"]["page"] - 1) / max_request_count) * 0.5)
        for performer in query_performers.get("performers"):
            performer_id = performer['id']
            if performer_id not in performercounts:
                performercounts[performer_id] = 1
            else:
                performercounts[performer_id] += 1
        performers.update([performer["id"] for performer in query_performers.get("performers")])
    return performers, performercounts


# Global to store Stash connection for local GraphQL calls
_stash_connection = None


def init_stash_connection(server_connection):
    """Initialize the Stash connection from the plugin input."""
    global _stash_connection
    
    # Handle 0.0.0.0 binding - can't connect TO 0.0.0.0, use localhost instead
    host = server_connection.get("Host", "localhost")
    if host == "0.0.0.0":
        host = "localhost"
    
    _stash_connection = {
        "url": server_connection.get("Scheme", "http") + "://" +
               host + ":" +
               str(server_connection.get("Port", 9999)) + "/graphql",
        "session_cookie": server_connection.get("SessionCookie", {}).get("Value"),
    }


def stash_graphql(query, variables=None):
    """Make a GraphQL request to local Stash instance."""
    global _stash_connection
    
    if not _stash_connection:
        log.error("Stash connection not initialized")
        return None
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # Use session cookie if available
    if _stash_connection.get("session_cookie"):
        headers["Cookie"] = f"session={_stash_connection['session_cookie']}"
    
    data = json.dumps({
        "query": query,
        "variables": variables or {}
    }).encode("utf-8")
    
    req = urllib.request.Request(_stash_connection["url"], data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("errors"):
                log.warning(f"Stash GraphQL errors: {result['errors']}")
            return result.get("data")
    except Exception as e:
        log.error(f"Stash request error: {e}")
        return None


def get_favorite_performers_stash_ids(endpoint: str):
    """Get stash_ids for all favorite performers linked to a specific stash-box endpoint.
    
    Uses Stash GraphQL API instead of direct database access.
    
    Args:
        endpoint: StashDB endpoint URL to match stash_ids against
        
    Returns:
        Set of StashDB IDs for favorites linked to that endpoint
    """
    query = """
    query FindFavoritePerformers($filter: FindFilterType) {
        findPerformers(
            filter: $filter
            performer_filter: { filter_favorites: true }
        ) {
            count
            performers {
                id
                name
                stash_ids {
                    endpoint
                    stash_id
                }
            }
        }
    }
    """
    
    stash_ids = set()
    page = 1
    per_page = 100
    
    while True:
        data = stash_graphql(query, {
            "filter": {
                "page": page,
                "per_page": per_page
            }
        })
        
        if not data or "findPerformers" not in data:
            break
        
        result = data["findPerformers"]
        performers = result.get("performers", [])
        
        if not performers:
            break
        
        for performer in performers:
            for sid in performer.get("stash_ids", []):
                if sid.get("endpoint") == endpoint:
                    stash_ids.add(sid.get("stash_id"))
        
        # Check if we've fetched all items
        total = result.get("count", 0)
        if page * per_page >= total:
            break
        
        page += 1
    
    log.info(f"Found {len(stash_ids)} favorite performers linked to {endpoint}")
    return stash_ids


def find_performer_by_stash_id(stash_id: str, endpoint: str):
    """Find a local performer by their stash_id.
    
    Args:
        stash_id: The StashDB performer ID
        endpoint: The StashDB endpoint URL
        
    Returns:
        Performer dict with id, name, and tag_ids, or None
    """
    # Stash doesn't have a direct way to query by stash_id, so we need to 
    # search performers that have stash_ids matching this endpoint
    query = """
    query FindPerformers($filter: FindFilterType) {
        findPerformers(filter: $filter) {
            count
            performers {
                id
                name
                tags {
                    id
                    name
                }
                stash_ids {
                    endpoint
                    stash_id
                }
            }
        }
    }
    """
    
    page = 1
    per_page = 100
    
    while True:
        data = stash_graphql(query, {
            "filter": {
                "page": page,
                "per_page": per_page
            }
        })
        
        if not data or "findPerformers" not in data:
            break
        
        result = data["findPerformers"]
        performers = result.get("performers", [])
        
        if not performers:
            break
        
        for performer in performers:
            for sid in performer.get("stash_ids", []):
                if sid.get("endpoint") == endpoint and sid.get("stash_id") == stash_id:
                    return {
                        "id": performer["id"],
                        "name": performer["name"],
                        "tag_ids": [tag["id"] for tag in performer.get("tags", [])]
                    }
        
        total = result.get("count", 0)
        if page * per_page >= total:
            break
        
        page += 1
    
    return None


def get_or_create_tag(tag_name: str):
    """Get or create a tag by name.
    
    Args:
        tag_name: Name of the tag to find or create
        
    Returns:
        Tag dict with id and name, or None
    """
    # First try to find the tag
    find_query = """
    query FindTag($name: String!) {
        findTags(tag_filter: { name: { value: $name, modifier: EQUALS } }) {
            tags {
                id
                name
            }
        }
    }
    """
    
    data = stash_graphql(find_query, {"name": tag_name})
    if data and "findTags" in data:
        tags = data["findTags"].get("tags", [])
        if tags:
            return tags[0]
    
    # Create the tag if it doesn't exist
    create_query = """
    mutation TagCreate($input: TagCreateInput!) {
        tagCreate(input: $input) {
            id
            name
        }
    }
    """
    
    log.info(f'Tag "{tag_name}" missing. Creating...')
    data = stash_graphql(create_query, {
        "input": {
            "name": tag_name,
            "description": "Tag created by Set Stashbox Favorite Performers plugin. Applied to performers found to have stash ids deleted from stashbox."
        }
    })
    
    if data and "tagCreate" in data:
        return data["tagCreate"]
    
    log.error(f"Failed to create tag: {tag_name}")
    return None


def tag_performer_by_stash_id(stash_id: str, endpoint: str, tag_id: str):
    """Tag a performer by their stash_id using GraphQL API.
    
    Args:
        stash_id: The StashDB performer ID
        endpoint: The StashDB endpoint URL
        tag_id: The ID of the tag to add
    """
    performer = find_performer_by_stash_id(stash_id, endpoint)
    if not performer:
        log.debug(f'Could not find performer with stash_id {stash_id}')
        return
    
    # Check if already tagged
    if tag_id in performer["tag_ids"]:
        log.debug(f'Performer already tagged {stash_id} {performer["id"]} {performer["name"]}')
        return
    
    # Add the tag using performerUpdate mutation
    update_query = """
    mutation PerformerUpdate($input: PerformerUpdateInput!) {
        performerUpdate(input: $input) {
            id
        }
    }
    """
    
    new_tag_ids = performer["tag_ids"] + [tag_id]
    
    data = stash_graphql(update_query, {
        "input": {
            "id": performer["id"],
            "tag_ids": new_tag_ids
        }
    })
    
    if data:
        log.debug(f'Tagging performer {stash_id} {performer["id"]} {performer["name"]}')
    else:
        log.warning(f'Failed to tag performer {stash_id} {performer["id"]}')


def set_stashbox_favorite_performers(server_connection, endpoint: str, boxapi_key: str, tag_errors: bool, tag_name: str):
    """Sync favorite performers between local Stash and StashDB.
    
    Uses GraphQL API instead of direct database access.
    
    Args:
        server_connection: Stash server connection info from plugin input
        endpoint: StashDB endpoint URL
        boxapi_key: StashDB API key
        tag_errors: Whether to tag performers with sync errors
        tag_name: Name of the tag to use for errors
    """
    # Initialize Stash connection for GraphQL calls
    init_stash_connection(server_connection)
    
    # Get favorite performers from local Stash via GraphQL
    stash_ids = get_favorite_performers_stash_ids(endpoint)
    
    log.info(f'Stashbox endpoint {endpoint}')
    log.info(f'Stash {len(stash_ids)} favorite performers')
    
    tag = None
    if tag_errors and tag_name:
        log.info(f'Tagging errors with performer tag: {tag_name}')
        tag = get_or_create_tag(tag_name)
    else:
        log.info(f'Not tagging errors')
    
    log.info(f'Fetching Stashbox favorite performers...')
    stashbox_stash_ids, performercounts = get_favorite_performers_from_stashbox(endpoint, boxapi_key)
    log.info(f'Stashbox {len(stashbox_stash_ids)} favorite performers')

    favorites_to_add = stash_ids - stashbox_stash_ids
    favorites_to_remove = stashbox_stash_ids - stash_ids
    dupes_to_remove = [[performer_id, count] for [performer_id, count] in performercounts.items() if count > 1]
    log.info(f'{len(favorites_to_add)} favorites to add')
    log.info(f'{len(favorites_to_remove)} favorites to remove')
    log.info(f'{len(dupes_to_remove)} duplicates to remove')
    total_work = len(favorites_to_add) + len(favorites_to_remove) + len(dupes_to_remove)
    
    if total_work == 0:
        log.info('Already in sync!')
        log.progress(1)
        return

    i = 0
    for stash_id in favorites_to_add:
        log.trace(f'Adding stashbox favorite {endpoint} {stash_id}')
        if not (update_stashbox_performer_favorite(endpoint, boxapi_key, stash_id, True) or {}).get('favoritePerformer'):
            log.warning(f'Failed adding stashbox favorite {stash_id}')
            if tag:
                tag_performer_by_stash_id(stash_id, endpoint, tag["id"])
        i += 1
        log.progress((i / total_work) * 0.5 + 0.5)
    log.info('Add done.')

    i = 0
    for stash_id in favorites_to_remove:
        log.trace(f'Removing stashbox favorite {endpoint} {stash_id}')
        if not (update_stashbox_performer_favorite(endpoint, boxapi_key, stash_id, False) or {}).get('favoritePerformer'):
            log.warning(f'Failed removing stashbox favorite {stash_id}')
            if tag:
                tag_performer_by_stash_id(stash_id, endpoint, tag["id"])
        i += 1
        log.progress((i / total_work) * 0.5 + 0.5)
    log.info('Remove done.')

    i = 0
    for performer_id, count in dupes_to_remove:
        log.trace(f'Fixing duplicate stashbox favorite {endpoint} {performer_id} count={count}')
        update_stashbox_performer_favorite(endpoint, boxapi_key, performer_id, False)
        update_stashbox_performer_favorite(endpoint, boxapi_key, performer_id, True)
        i += 1
        log.progress((i / total_work) * 0.5 + 0.5)
    log.info('Fixed duplicates.')
    log.progress(1)

def set_stashbox_favorite_performer(endpoint, boxapi_key, stash_id, favorite):
    if not stash_id:
        log.warning(f'Empty stash_id provided, skipping performer sync')
        return
    result = get_stashbox_performer_favorite(endpoint, boxapi_key, stash_id)
    if not result:
        return
    if not result.get("findPerformer"):
        log.warning(f'Performer not found on stashbox: {stash_id}')
        return
    if favorite != result["findPerformer"]["is_favorite"]:
        update_stashbox_performer_favorite(endpoint, boxapi_key, stash_id, favorite)
        log.info(f'Updated Stashbox performer {stash_id} favorite={favorite}')
    else:
        log.info(f'Stashbox performer {stash_id} already in sync favorite={favorite}')


# ============ STUDIO SYNC FUNCTIONS ============

def get_stashbox_studio_favorite(endpoint, boxapi_key, stash_id):
    query = """
query FullStudio($id: ID!) {
  findStudio(id: $id) {
    id
    is_favorite
  }
}
    """

    variables = {
        "id": stash_id
    }

    return stashbox_call_graphql(endpoint, boxapi_key, query, variables)


def update_stashbox_studio_favorite(endpoint: str, boxapi_key: str, stash_id: str, favorite: bool):
    query = """
mutation FavoriteStudio($id: ID!, $favorite: Boolean!) {
  favoriteStudio(id: $id, favorite: $favorite)
}
"""

    variables = {
        "id": stash_id,
        "favorite": favorite
    }

    return stashbox_call_graphql(endpoint, boxapi_key, query, variables)


def get_favorite_studios_from_stashbox(endpoint: str, boxapi_key: str):
    query = """
query Studios($input: StudioQueryInput!) {
  queryStudios(input: $input) {
    count
    studios {
      id
      is_favorite
    }
  }
}
"""

    per_page = 100

    variables = {
        "input": {
            "names": "",
            "is_favorite": True,
            "page": 1,
            "per_page": per_page,
            "sort": "NAME",
            "direction": "ASC"
        }
    }

    studios = set()

    total_count = None
    request_count = 0
    max_request_count = 1

    studiocounts = {}

    while request_count < max_request_count:
        result = stashbox_call_graphql(endpoint, boxapi_key, query, variables)
        request_count += 1
        variables["input"]["page"] += 1
        if not result:
            break
        query_studios = result.get("queryStudios")
        if not query_studios:
            break
        if total_count is None:
            total_count = query_studios.get("count")
            max_request_count = math.ceil(total_count / per_page)

        log.info(f'Received page {variables["input"]["page"] - 1} of {max_request_count}')
        log.progress(((variables["input"]["page"] - 1) / max_request_count) * 0.5)
        for studio in query_studios.get("studios"):
            studio_id = studio['id']
            if studio_id not in studiocounts:
                studiocounts[studio_id] = 1
            else:
                studiocounts[studio_id] += 1
        studios.update([studio["id"] for studio in query_studios.get("studios")])
    return studios, studiocounts


def get_favorite_studios_stash_ids(endpoint: str):
    """Get stash_ids for all favorite studios linked to a specific stash-box endpoint.
    
    Uses Stash GraphQL API instead of direct database access.
    
    Args:
        endpoint: StashDB endpoint URL to match stash_ids against
        
    Returns:
        Set of StashDB IDs for favorites linked to that endpoint
    """
    query = """
    query FindFavoriteStudios($filter: FindFilterType) {
        findStudios(
            filter: $filter
            studio_filter: { is_missing: null }
        ) {
            count
            studios {
                id
                name
                favorite
                stash_ids {
                    endpoint
                    stash_id
                }
            }
        }
    }
    """
    
    stash_ids = set()
    page = 1
    per_page = 100
    
    while True:
        data = stash_graphql(query, {
            "filter": {
                "page": page,
                "per_page": per_page
            }
        })
        
        if not data or "findStudios" not in data:
            break
        
        result = data["findStudios"]
        studios = result.get("studios", [])
        
        if not studios:
            break
        
        for studio in studios:
            # Only include favorite studios
            if not studio.get("favorite"):
                continue
            for sid in studio.get("stash_ids", []):
                if sid.get("endpoint") == endpoint:
                    stash_ids.add(sid.get("stash_id"))
        
        # Check if we've fetched all items
        total = result.get("count", 0)
        if page * per_page >= total:
            break
        
        page += 1
    
    log.info(f"Found {len(stash_ids)} favorite studios linked to {endpoint}")
    return stash_ids


def find_studio_by_stash_id(stash_id: str, endpoint: str):
    """Find a local studio by their stash_id.
    
    Args:
        stash_id: The StashDB studio ID
        endpoint: The StashDB endpoint URL
        
    Returns:
        Studio dict with id, name, and tag_ids, or None
    """
    query = """
    query FindStudios($filter: FindFilterType) {
        findStudios(filter: $filter) {
            count
            studios {
                id
                name
                tags {
                    id
                    name
                }
                stash_ids {
                    endpoint
                    stash_id
                }
            }
        }
    }
    """
    
    page = 1
    per_page = 100
    
    while True:
        data = stash_graphql(query, {
            "filter": {
                "page": page,
                "per_page": per_page
            }
        })
        
        if not data or "findStudios" not in data:
            break
        
        result = data["findStudios"]
        studios = result.get("studios", [])
        
        if not studios:
            break
        
        for studio in studios:
            for sid in studio.get("stash_ids", []):
                if sid.get("endpoint") == endpoint and sid.get("stash_id") == stash_id:
                    return {
                        "id": studio["id"],
                        "name": studio["name"],
                        "tag_ids": [tag["id"] for tag in studio.get("tags", [])]
                    }
        
        total = result.get("count", 0)
        if page * per_page >= total:
            break
        
        page += 1
    
    return None


def tag_studio_by_stash_id(stash_id: str, endpoint: str, tag_id: str):
    """Tag a studio by their stash_id using GraphQL API.
    
    Args:
        stash_id: The StashDB studio ID
        endpoint: The StashDB endpoint URL
        tag_id: The ID of the tag to add
    """
    studio = find_studio_by_stash_id(stash_id, endpoint)
    if not studio:
        log.debug(f'Could not find studio with stash_id {stash_id}')
        return
    
    # Check if already tagged
    if tag_id in studio["tag_ids"]:
        log.debug(f'Studio already tagged {stash_id} {studio["id"]} {studio["name"]}')
        return
    
    # Add the tag using studioUpdate mutation
    update_query = """
    mutation StudioUpdate($input: StudioUpdateInput!) {
        studioUpdate(input: $input) {
            id
        }
    }
    """
    
    new_tag_ids = studio["tag_ids"] + [tag_id]
    
    data = stash_graphql(update_query, {
        "input": {
            "id": studio["id"],
            "tag_ids": new_tag_ids
        }
    })
    
    if data:
        log.debug(f'Tagging studio {stash_id} {studio["id"]} {studio["name"]}')
    else:
        log.warning(f'Failed to tag studio {stash_id} {studio["id"]}')


def set_stashbox_favorite_studios(server_connection, endpoint: str, boxapi_key: str, tag_errors: bool, tag_name: str):
    """Sync favorite studios between local Stash and StashDB.
    
    Uses GraphQL API instead of direct database access.
    
    Args:
        server_connection: Stash server connection info from plugin input
        endpoint: StashDB endpoint URL
        boxapi_key: StashDB API key
        tag_errors: Whether to tag studios with sync errors
        tag_name: Name of the tag to use for errors
    """
    # Initialize Stash connection for GraphQL calls
    init_stash_connection(server_connection)
    
    # Get favorite studios from local Stash via GraphQL
    stash_ids = get_favorite_studios_stash_ids(endpoint)
    
    log.info(f'Stashbox endpoint {endpoint}')
    log.info(f'Stash {len(stash_ids)} favorite studios')
    
    tag = None
    if tag_errors and tag_name:
        log.info(f'Tagging errors with tag: {tag_name}')
        tag = get_or_create_tag(tag_name)
    else:
        log.info(f'Not tagging errors')
    
    log.info(f'Fetching Stashbox favorite studios...')
    stashbox_stash_ids, studiocounts = get_favorite_studios_from_stashbox(endpoint, boxapi_key)
    log.info(f'Stashbox {len(stashbox_stash_ids)} favorite studios')

    favorites_to_add = stash_ids - stashbox_stash_ids
    favorites_to_remove = stashbox_stash_ids - stash_ids
    dupes_to_remove = [[studio_id, count] for [studio_id, count] in studiocounts.items() if count > 1]
    log.info(f'{len(favorites_to_add)} favorites to add')
    log.info(f'{len(favorites_to_remove)} favorites to remove')
    log.info(f'{len(dupes_to_remove)} duplicates to remove')
    total_work = len(favorites_to_add) + len(favorites_to_remove) + len(dupes_to_remove)
    
    if total_work == 0:
        log.info('Already in sync!')
        log.progress(1)
        return

    i = 0
    for stash_id in favorites_to_add:
        log.trace(f'Adding stashbox favorite {endpoint} {stash_id}')
        if not (update_stashbox_studio_favorite(endpoint, boxapi_key, stash_id, True) or {}).get('favoriteStudio'):
            log.warning(f'Failed adding stashbox favorite studio {stash_id}')
            if tag:
                tag_studio_by_stash_id(stash_id, endpoint, tag["id"])
        i += 1
        log.progress((i / total_work) * 0.5 + 0.5)
    log.info('Add done.')

    i = 0
    for stash_id in favorites_to_remove:
        log.trace(f'Removing stashbox favorite {endpoint} {stash_id}')
        if not (update_stashbox_studio_favorite(endpoint, boxapi_key, stash_id, False) or {}).get('favoriteStudio'):
            log.warning(f'Failed removing stashbox favorite studio {stash_id}')
            if tag:
                tag_studio_by_stash_id(stash_id, endpoint, tag["id"])
        i += 1
        log.progress((i / total_work) * 0.5 + 0.5)
    log.info('Remove done.')

    i = 0
    for studio_id, count in dupes_to_remove:
        log.trace(f'Fixing duplicate stashbox favorite {endpoint} {studio_id} count={count}')
        update_stashbox_studio_favorite(endpoint, boxapi_key, studio_id, False)
        update_stashbox_studio_favorite(endpoint, boxapi_key, studio_id, True)
        i += 1
        log.progress((i / total_work) * 0.5 + 0.5)
    log.info('Fixed duplicates.')
    log.progress(1)


def set_stashbox_favorite_studio(endpoint, boxapi_key, stash_id, favorite):
    if not stash_id:
        log.warning(f'Empty stash_id provided, skipping studio sync')
        return
    result = get_stashbox_studio_favorite(endpoint, boxapi_key, stash_id)
    if not result:
        return
    if not result.get("findStudio"):
        log.warning(f'Studio not found on stashbox: {stash_id}')
        return
    if favorite != result["findStudio"]["is_favorite"]:
        update_stashbox_studio_favorite(endpoint, boxapi_key, stash_id, favorite)
        log.info(f'Updated Stashbox studio {stash_id} favorite={favorite}')
    else:
        log.info(f'Stashbox studio {stash_id} already in sync favorite={favorite}')
