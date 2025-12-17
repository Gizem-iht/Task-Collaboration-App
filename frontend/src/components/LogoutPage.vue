.<template>
  <div style="max-width: 400px; margin: 50px auto; text-align: center;">
    <h2 style="font-size: 28px; margin-bottom: 20px;">Logout Panel</h2>

    <p>Oturumunuzu kapatmak için aşağıdaki butona basın.</p>

    <button
      @click="goLogin"
      style="
        margin-top: 20px;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
      "
    >
      Logout
    </button>
  </div>
</template>

<script>
export default {
  name: "LogoutPage",
  methods: {
    goLogin() {
      // Şimdilik SADECE login sayfasına götürüyoruz
      this.$router.push("/login");
    },
  },
};
</script>
