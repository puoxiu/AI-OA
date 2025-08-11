import axios from "axios"


class Http{
    constructor() {
        this.instance = axios.create({
            // baseURL: "http://127.0.0.1:8003/api/v1",
            // timeout: 5000
            baseURL: import.meta.env.VITE_BASE_URL,
            timeout: import.meta.env.VITE_TIMEOUT
        });
    }

    async post(path, data) {
        // path: /user/login
        // url: http://127.0.0.1:8003/api/v1/user/login
        // return this.instance.post(path, data)
        // 异步
        return new Promise(async (resolve, reject) => {
            try{
                let result = await this.instance.post(path, data)
                resolve(result)
            }catch(err) {
                let msg_data = err.response.data
                reject(msg_data)
            }
        })
    }

    get(path, params) {
        return this.instance.get(path, params)
    }
}

export default new Http()