import http from "./http";

// 获取部门列表
const getAllDepartment = () => {
    return http.get("/department/all")
}



export default {
    getAllDepartment
}