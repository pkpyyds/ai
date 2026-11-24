import { defineStore } from 'pinia'
import { api } from '../api/workspace'

export const useWorkspace = defineStore('workspace', {
  state: () => ({ health: null, pool: [], candidates: [], jobs: [], logs: [], loading: false, error: '', notice: '' }),
  actions: {
    async refresh() {
      this.loading = true; this.error = ''
      try {
        this.health = await api.health()
        if (!this.health.demo_mode) { this.pool = []; this.candidates = []; this.jobs = []; this.logs = []; this.error = '后端未启用演示模式，业务接口默认关闭。'; return }
        const [pool, candidates, jobs, logs] = await Promise.all([api.pool(), api.candidates(), api.jobs(), api.logs()])
        Object.assign(this, { pool, candidates, jobs, logs })
      } catch (error) { this.error = error.message } finally { this.loading = false }
    },
    async review(id, approved, comment) {
      this.error = ''; this.notice = ''
      try { await api.review(id, approved, comment); this.notice = '演示核验已保存；没有调用任何外部平台。'; await this.refresh(); return true }
      catch (error) { this.error = error.message; return false }
    },
  },
})
