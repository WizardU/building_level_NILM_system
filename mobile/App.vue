<script>
export default {
  onLaunch() {
    const token = uni.getStorageSync('access_token')
    if (!token) {
      uni.reLaunch({ url: '/pages/login/login' })
    }
  }
}
</script>

<style>
page { background: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
</style>
