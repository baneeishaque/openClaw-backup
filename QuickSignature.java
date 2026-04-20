/**
 * 快速签名生成 - 最简版本
 */
public class QuickSignature {
    
    public static String generate(String appKey, String appSecret, String body, 
                                 String timestamp, String version) throws Exception {
        // 构建参数Map（TreeMap自动排序）
        java.util.Map<String, String> params = new java.util.TreeMap<>();
        params.put("appKey", appKey);
        params.put("body", body);
        params.put("timestamp", timestamp);
        params.put("version", version);
        
        // 拼接字符串
        StringBuilder sb = new StringBuilder();
        for (java.util.Map.Entry<String, String> entry : params.entrySet()) {
            sb.append(entry.getKey()).append(entry.getValue());
        }
        
        // 添加秘钥并计算MD5
        String signStr = appSecret + sb.toString() + appSecret;
        java.security.MessageDigest md = java.security.MessageDigest.getInstance("MD5");
        byte[] digest = md.digest(signStr.getBytes("UTF-8"));
        StringBuilder result = new StringBuilder();
        for (byte b : digest) {
            result.append(String.format("%02x", b & 0xff));
        }
        return result.toString();
    }
    
    public static void main(String[] args) throws Exception {
        // 你的示例参数
        String appKey = "123456";
        String appSecret = "abcdefg123";
        String body = "{\"order_id\":\"20170301000001\"}";
        String timestamp = "1488363493";
        String version = "1.0";
        
        String signature = generate(appKey, appSecret, body, timestamp, version);
        System.out.println("=== 快速签名生成 ===");
        System.out.println("参数:");
        System.out.println("  appKey: " + appKey);
        System.out.println("  body: " + body);
        System.out.println("  timestamp: " + timestamp);
        System.out.println("  version: " + version);
        System.out.println("\n最终签名:");
        System.out.println("  " + signature);
        
        // 如果你想验证这个签名是否和你的服务端一致
        System.out.println("\n签名字符串:");
        System.out.println("  abcdefg123appKey123456body{\"order_id\":\"20170301000001\"}timestamp1488363493version1.0abcdefg123");
        System.out.println("MD5结果应该相同");
    }
}