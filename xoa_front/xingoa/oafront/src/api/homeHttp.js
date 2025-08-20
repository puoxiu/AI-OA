import http from "./http"

// 最新通知
const getLatestInforms = () => {
    return http.get(`/home/latest/inform`)
}

// 最新考勤
const getLatestAbsents = () => {
    return http.get(`/home/latest/absent`)
}

// 部门员工数量统计
const getDepartmentStaffCount = () => {
    return http.get(`/home/department/staff/count`)
}

export default {    
    getLatestInforms,
    getLatestAbsents,
    getDepartmentStaffCount
}