import http from "./http";

// 获取请假类型
const getAbsentTypes = () => {
    return http.get("/absent/type")
}

// 获取审批人
const getResponder = () => {
    return http.get("/absent/responder")
}

// 发起请假
const addAbsent = (data) => {
    return http.post("/absent/add", data)
}

// 获取请假列表
// const getMyAbsents = (page=1, page_size=10) => {
//     return http.get("/absent/my_absents", {page, page_size})
// }
// pageSize前端必须是10
const getMyAbsents = (page=1) => {
    // return http.get("/absent/my_absents", {page, page_size: 10})
    let path = `/absent/my_absents?page=${page}&page_size=10`
    return http.get(path)
}

const getSubAbsents = (page=1) => {
    let path = `/absent/my_all_staffs_absents?page=${page}&page_size=10`
    return http.get(path)
}

// 处理下属请假
const handleSubAbsent = (absent_id, status, response_content) => {
  // 路径中包含资源ID，参数放在body
  return http.patch(`/absent/my_staffs_absents/${absent_id}`, {
    status,
    response_content
  })
}



export default {
    getAbsentTypes, getResponder, addAbsent, getMyAbsents, handleSubAbsent, getSubAbsents
}