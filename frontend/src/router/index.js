import { createRouter, createWebHistory } from 'vue-router'
import WorkspaceView from '../views/WorkspaceView.vue'

export const navigation = [
  { path: '/', key: 'dashboard', icon: '▦', title: '工作台' },
  { path: '/pool', key: 'pool', icon: '▧', title: '商品池' },
  { path: '/candidates', key: 'candidates', icon: '◇', title: '候选池' },
  { path: '/content-jobs', key: 'content', icon: '✦', title: '内容生成' },
  { path: '/content-reviews', key: 'review', icon: '☑', title: '内容审核' },
  { path: '/listing-jobs', key: 'listing', icon: '↗', title: '上架任务' },
  { path: '/selection-rules', key: 'rules', icon: '⚙', title: '筛选规则' },
  { path: '/audit-rules', key: 'audit', icon: '≡', title: '审核逻辑' },
  { path: '/crawl-tasks', key: 'crawl', icon: '◷', title: '采集任务' },
  { path: '/audit-logs', key: 'logs', icon: '▤', title: '操作审计' },
]
export default createRouter({ history: createWebHistory(), routes: navigation.map(item => ({ path: item.path, component: WorkspaceView, meta: item })), scrollBehavior: () => ({ top: 0 }) })
