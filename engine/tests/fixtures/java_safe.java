@CrossOrigin(origins = "https://app.example.com")
class S {
  PreparedStatement ps = conn.prepareStatement("SELECT * FROM u WHERE id = ?");
  MessageDigest md = MessageDigest.getInstance("SHA-256");
  Statement st2 = conn.createStatement();
  String del = "DELETE FROM t WHERE id = ?";
  ResultSet rs = conn.createStatement().executeQuery("SELECT 1");
}
