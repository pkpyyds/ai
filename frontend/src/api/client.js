import axios from 'axios'
// Relative URL: the dev server / Nginx forwards requests to the API.
export const client = axios.create({ baseURL: '/api/v1', timeout: 10000 })
export async function request(method, path, data) {
  try {
    const response = await client.request({ method, url: path, data })
    return response.data.data
  } catch (error) {
    throw new Error(error.response?.data?.message || '无法连接后端服务，请检查 API 是否启动。')
  }
}
