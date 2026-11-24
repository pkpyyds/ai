import { request } from './client'
export const api = {
  health: () => request('GET', '/health'),
  pool: () => request('GET', '/products/pool'),
  candidates: () => request('GET', '/products/candidates'),
  jobs: () => request('GET', '/content-jobs'),
  logs: () => request('GET', '/audit-logs'),
  review: (id, approved, comment) => request('POST', `/reviews/${id}/${approved ? 'approve' : 'reject'}`, { comment }),
}
