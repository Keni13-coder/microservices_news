from .page_not_found import not_found
from .access_denied import no_access
from .something_wrong import server_error

exception_handlers = {
    403: no_access,
    404: not_found,
    500: server_error,
}