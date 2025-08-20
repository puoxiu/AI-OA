import http from "./http";

// 发布通知
const publishInform = (data) => {
    return http.post("/inform/create_inform", data)
}

// 获取通知列表
const getInformList = () => {
    return http.get(`/inform/all`)
}

// 删除通知
const deleteInform = (inform_id) => {
    return http.delete(`/inform/delete_by_id/${inform_id}`)
}

// 获取通知详情
const getInformDetail = (inform_id) => {
    return http.get(`/inform/${inform_id}`)
}

export default {
    publishInform,
    getInformList,
    deleteInform,
    getInformDetail,
}