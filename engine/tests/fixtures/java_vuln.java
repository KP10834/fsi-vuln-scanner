@CrossOrigin("*")
class V {
  String q = "SELECT * FROM u WHERE id = " + id;
  Statement st = conn.createStatement();
  MessageDigest md = MessageDigest.getInstance("MD5");
  Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
}
