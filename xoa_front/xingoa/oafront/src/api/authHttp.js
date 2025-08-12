import http from "./http"

const login = (email, password) => {
    return http.post("/user/login", {
        email,
        password
    })
}

const resetPwd = (verifyCode, newPwd1, newPwd2) => {
    return http.post("/user/resetpwd", {
        verify_code: verifyCode,
        new_pwd1: newPwd1,
        new_pwd2: newPwd2
    })
}

export default {
    login,
    resetPwd
}