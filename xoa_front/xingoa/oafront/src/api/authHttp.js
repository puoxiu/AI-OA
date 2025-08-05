import http from "./http"

const login = (email, password) => {
    return http.post("/user/login", {
        email,
        password
    })
}


export default {
    login
}