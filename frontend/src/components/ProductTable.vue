<script setup>
defineProps({ products: { type: Array, required: true }, stage: { type: String, required: true } })
defineEmits(['review'])
</script>
<template>
  <div class="table-wrap"><table><thead><tr><th>商品信息</th><th>类目</th><th>来源</th><th>状态</th><th>操作</th></tr></thead><tbody>
    <tr v-for="(product, index) in products" :key="product.id"><td><div class="prod"><span class="thumb">{{ ['◧','◒','▣','⌁'][index % 4] }}</span><div><b>{{ product.title }}</b><small>{{ product.platform_product_id }} · 示例商品</small></div></div></td><td>{{ product.category }}</td><td>演示数据</td><td><span class="badge amber">{{ stage === 'first' ? '待初核' : '待复核' }}</span></td><td><button v-if="product.task_id" class="link" @click="$emit('review', product)">查看并核验 →</button><span v-else>无待处理任务</span></td></tr>
    <tr v-if="!products.length"><td colspan="5" class="empty">暂无示例商品</td></tr>
  </tbody></table></div>
</template>
