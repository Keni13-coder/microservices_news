let {token, user} = sessionStorage


let authHtmlForLoginUser = (username) => `<li class="nav-item"><a class="nav-link" id="logout_link" href="/logout/${username}">Logout</a></li>
<li class="nav-item"><a href="/update/" class="nav-link">${username}</a></li>`
let authHtmlForUnknownUser = `<li class="nav-item"><a class="nav-link" href="/login/">Login</a></li>
              <li class="nav-item"><a class="nav-link" href="/register/">Register</a></li>`

const link_items = document.querySelector('#auth_links')
if (token && user) {

    link_items.innerHTML = authHtmlForLoginUser(user)
    document.querySelector('#logout_link').addEventListener('click', () => {
        sessionStorage.clear()
    })
} else {
    link_items.innerHTML = authHtmlForUnknownUser
}