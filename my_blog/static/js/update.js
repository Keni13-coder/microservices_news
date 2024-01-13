let form_el = document.querySelector('#signup-form')


form_el.addEventListener('submit', (e) => {
    e.preventDefault()
    let form = new FormData(e.target),
        username = form.get('username'),
        email = form.get('email'),
        old_user_name = sessionStorage.getItem('user'),
        data = {
            username: username,
            email: email,
            old: old_user_name
        }


    postData(`/update/`, data).then(response => {

        if (response.status === 'success') {
            sessionStorage.setItem('user', response.user)
            window.location.replace('/')
        } else {
            let err_list = JSON.parse(response.errors)
            alert(err_list[0])

        }

    })
})

function postData(url = ``, data = {}) {
    return fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json()); // parses response to JSON
}