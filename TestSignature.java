/**
 * 签名测试类
 */
public class TestSignature {
    
    public static void main(String[] args) {
        System.out.println("======= 签名测试 =======");
        
        // 使用你的示例参数
        String appKey = "123456";
        String appSecret = "abcdefg123";
        String body = "{\"order_id\":\"20170301000001\"}";
        String timestamp = "1488363493";
        String version = "1.0";
        
        // 步骤演示
        System.out.println("\n【步骤演示】");
        System.out.println("1. 排序后参数顺序: appKey, body, timestamp, version");
        System.out.println("2. 拼接字符串: ");
        String concatStr = "appKey123456body{\"order_id\":\"20170301000001\"}timestamp1488363493version1.0";
        System.out.println("   " + concatStr);
        System.out.println("3. 添加秘钥: ");
        String signStr = "abcdefg123appKey123456body{\"order_id\":\"20170301000001\"}timestamp1488363493version1.0abcdefg123";
        System.out.println("   " + signStr);
        
        // 计算MD5
        String signature = SignatureGenerator.md5(signStr);
        System.out.println("\n【最终结果】");
        System.out.println("签名 (32位MD5): " + signature);
        System.out.println("签名长度: " + signature.length() + " 位");
        
        // 使用工具类验证
        System.out.println("\n【工具类验证】");
        SignatureGenerator signer = new SignatureGenerator(appKey, appSecret);
        String generated = signer.generateSignature(body, timestamp, version);
        System.out.println("工具类生成签名: " + generated);
        
        if (signature.equals(generated)) {
            System.out.println("✅ 签名验证成功！");
        } else {
            System.out.println("❌ 签名验证失败！");
        }
    }
}