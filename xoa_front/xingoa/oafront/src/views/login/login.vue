<script setup name="login">
import login_img from "@/assets/images/login.png"
import { reactive } from "vue"
import { useAuthStore } from "@/stores/auth"
import { useRouter } from "vue-router"
import authHttp from "@/api/authHttp"
import { ElMessage } from 'element-plus'



const authStore = useAuthStore()
const router = useRouter()



let form = reactive({
    email: "",
    password: ""
})

const onSubmit = async () => {
    // 正则表达式
    const reg = /^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$/
    if (!reg.test(form.email)) {
        // alert("请输入正确的邮箱")
        ElMessage.error("请输入正确的邮箱格式")

        return
    }
    if (form.password.length < 6) {
        ElMessage.error("密码不能少于6位")

        return
    }
    // axios
    // 1简单版本
    // axios.post("http://127.0.0.1:8003/api/v1/user/login", form).then(res => {
    //     let data = res.data
    //     let token = data.token
    //     authStore.setToken(token)
    //     // 跳转
    //     router.push({ name: "frame" })

    // }).catch(err => {
    //     console.log("登录失败")
    //     console.log(err.response.data)
    // })

    // 2优雅版本
    // authHttp.login(form.email, form.password).then(res => {
    //     let data = res.data
    //     let token = data.token
    //     authStore.setToken(token)
    //     // 跳转
    //     router.push({ name: "frame" })
    // }).catch(err => {
    //     console.log("登录失败")
    //     console.log(err.response.data)
    // })

    // 3 优雅异步版本
    try{
        let result = await authHttp.login(form.email, form.password)
        let token = result.data.token
        authStore.setToken(token)
        // 跳转
        router.push({ name: "frame" })
    }catch(err) {
        console.log(err)
        // alert(err)
        ElMessage.error(err.msg)
        console.log(err.code)
    }

}


</script>

<template>
    <div class="dowebok">
        <div class="container-login100">
            <div class="wrap-login100">
                <div class="login100-pic js-tilt" data-tilt>
                    <img :src="login_img" alt="IMG" />
                </div>

                <div class="login100-form validate-form">
                    <span class="login100-form-title"> 员工登陆 </span>

                    <div class="wrap-input100 validate-input">
                        <input class="input100" type="text" name="email" placeholder="邮箱"  v-model="form.email" />

                        <span class="focus-input100"></span>
                        <span class="symbol-input100">
                            <i class="iconfont icon-fa-envelope" aria-hidden="true"></i>
                        </span>
                    </div>

                    <div class="wrap-input100 validate-input">
                        <input class="input100" type="password" name="password" placeholder="密码"  v-model="form.password" />

                        <span class="focus-input100"></span>
                        <span class="symbol-input100">
                            <i class="iconfont icon-fa-lock" aria-hidden="true"></i>
                        </span>
                    </div>

                    <div class="container-login100-form-btn">
                        <button class="login100-form-btn" @click="onSubmit">
                            登陆
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped src="@/assets/css/login.css"></style>
<style scoped src="@/assets/iconfont/iconfont.css"></style>