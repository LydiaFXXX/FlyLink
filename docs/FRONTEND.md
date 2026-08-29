# 前端美化升级说明

业务后端逻辑未改动，以下为样式 / 布局 / 动效相关文件。

## 设计系统

- `frontend/src/styles/theme.css`  
  深空蓝 `#0A1628` + 科技灰 `#E8EEF5` + 淡青 `#00D4C8`  
  自定义滚动条、页面淡入淡出、毛玻璃弹窗、按钮 hover 缩放、Element Plus 主题变量覆盖

## 布局与首页

- `frontend/src/layouts/MainLayout.vue` — 固定悬浮顶栏、Logo「FlyLink飞链」、四大入口、移动端抽屉
- `frontend/src/views/home/HomeView.vue` — 大屏风首页、数据卡片动效、雷达视觉、三大模块入口

## 业务页（视觉升级）

| 模块 | 文件 | 升级点 |
|------|------|--------|
| 发单 | `views/orders/PublishOrder.vue` | 分步卡片、地图点位选址、浮动表单 |
| 抢单 | `views/orders/OrderHall.vue` | 卡片列表、距离/紧急/资质标签、渐变底色 |
| 订单 | `views/orders/OrderDetail.vue` | 流程步骤条、轨迹可视化、素材预览 |
| 招聘 | `views/jobs/JobList.vue` | 薪资高亮、彩色徽章标签 |
| 简历 | `views/jobs/ResumeView.vue` | 折叠分区、作品集缩略图 |
| 沟通 | `views/jobs/ChatView.vue` | IM 气泡、签约/中介费状态 |
| 租赁商城 | `views/rental/DeviceMall.vue` | 网格卡片、参数折叠、租金/押金区分 |
| 租赁下单 | `views/rental/RentalCheckout.vue` | 四步步骤条、信用免押提示 |

## 字体

`frontend/index.html` 引入 Orbitron（品牌数字）+ Noto Sans SC（正文）
