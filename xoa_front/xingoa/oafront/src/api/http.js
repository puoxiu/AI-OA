import axios from "axios"
import { useAuthStore } from "@/stores/auth"

class Http{
    constructor() {
        this.instance = axios.create({
            // baseURL: "http://127.0.0.1:8003/api/v1",
            // timeout: 5000
            baseURL: import.meta.env.VITE_BASE_URL,
            timeout: import.meta.env.VITE_TIMEOUT
        });
        // 请求拦截器--添加token
        this.instance.interceptors.request.use(
            (config) => {
                const authStore = useAuthStore()
                if(authStore.token) {
                    config.headers.Authorization = `Bearer ${authStore.token}`
                }
                return config
            },
            (error) => {
                return Promise.reject(error)
            }
        )

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
        return new Promise(async (resolve, reject) => {
            try{
                let result = await this.instance.get(path, params)
                resolve(result)
            }catch(err) {
                let msg_data = err.response.data
                reject(msg_data)
            }
        })
    }

    patch(path, data) {
        return new Promise(async (resolve, reject) => {
            try{
                let result = await this.instance.patch(path, data)
                resolve(result)
            }catch(err) {
                let msg_data = err.response.data
                reject(msg_data)
            }
        })
    }

    delete(path) {
        return new Promise(async (resolve, reject) => {
            try{
                let result = await this.instance.delete(path);
                resolve(result);
            }catch(err) {
                let msg_data = err.response.data; 
                reject(msg_data || { msg: "请求失败" }); // 兜底错误信息
            }
        })
    }
}

export default new Http()