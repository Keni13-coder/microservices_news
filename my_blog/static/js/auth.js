let form_el = document.querySelector('#signup-form')


form_el.addEventListener('submit', (e) => {
    e.preventDefault()
    let form = new FormData(e.target),
        username = form.get('username'),
        password = form.get('password'),
        data = {
            username: username,
            password: password
        }


    postData('/login/', data).then(response => {
        if (response.status === 'success') {
            sessionStorage.setItem('token', response.token)
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