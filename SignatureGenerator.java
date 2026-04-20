import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;

/**
 * API签名生成工具类
 * 支持字典排序、参数拼接、MD5加密生成签名
 * 
 * @author OpenClaw
 * @date 2026-03-31
 */
public class SignatureGenerator {
    
    private String appKey;
    private String appSecret;
    
    /**
     * 构造函数
     * @param appKey 应用Key
     * @param appSecret 应用密钥
     */
    public SignatureGenerator(String appKey, String appSecret) {
        this.appKey = appKey;
        this.appSecret = appSecret;
    }
    
    /**
     * 生成签名
     * @param body 请求体数据（JSON格式字符串）
     * @param timestamp 时间戳
     * @param version 版本号
     * @return 32位MD5签名字符串
     */
    public String generateSignature(String body, String timestamp, String version) {
        // 第一步：构建参数并字典排序
        Map<String, String> params = new TreeMap<>(); // TreeMap自动按key排序
        params.put("appKey", appKey);
        if (body != null && !body.isEmpty()) {
            params.put("body", body);
        }
        params.put("timestamp", timestamp);
        params.put("version", version);
        
        // 第二步：拼接key和value
        StringBuilder concatStr = new StringBuilder();
        for (Map.Entry<String, String> entry : params.entrySet()) {
            concatStr.append(entry.getKey()).append(entry.getValue());
        }
        
        // 第三步：首尾添加appSecret
        String signStr = appSecret + concatStr.toString() + appSecret;
        
        // 第四步：MD5加密
        return md5Encrypt(signStr);
    }
    
    /**
     * 生成签名（重载方法，自动生成时间戳）
     * @param body 请求体数据（JSON格式字符串）
     * @param version 版本号
     * @return 32位MD5签名字符串
     */
    public String generateSignature(String body, String version) {
        String timestamp = String.valueOf(System.currentTimeMillis() / 1000);
        return generateSignature(body, timestamp, version);
    }
    
    /**
     * 生成签名（重载方法，默认版本1.0）
     * @param body 请求体数据（JSON格式字符串）
     * @param timestamp 时间戳
     * @return 32位MD5签名字符串
     */
    public String generateSignature(String body, String timestamp) {
        return generateSignature(body, timestamp, "1.0");
    }
    
    /**
     * 验证签名是否正确
     * @param signature 待验证的签名
     * @param body 请求体数据
     * @param timestamp 时间戳
     * @param version 版本号
     * @return 签名是否匹配
     */
    public boolean verifySignature(String signature, String body, String timestamp, String version) {
        String generated = generateSignature(body, timestamp, version);
        return generated.equalsIgnoreCase(signature);
    }
    
    /**
     * MD5加密
     * @param text 待加密字符串
     * @return 32位MD5字符串（小写）
     */
    private String md5Encrypt(String text) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(text.getBytes());
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                sb.append(String.format("%02x", b & 0xff));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5加密失败", e);
        }
    }
    
    // ==================== 工具方法（可单独调用）====================
    
    /**
     * 第一步：字典排序
     * @param params 参数Map
     * @return 排序后的key列表
     */
    public static List<String> sortParams(Map<String, String> params) {
        List<String> keys = new ArrayList<>(params.keySet());
        Collections.sort(keys);
        return keys;
    }
    
    /**
     * 第二步：拼接参数
     * @param params 参数Map
     * @param sortedKeys 排序后的key列表
     * @return 拼接后的字符串
     */
    public static String concatParams(Map<String, String> params, List<String> sortedKeys) {
        StringBuilder result = new StringBuilder();
        for (String key : sortedKeys) {
            result.append(key).append(params.get(key));
        }
        return result.toString();
    }
    
    /**
     * 第三步：添加秘钥
     * @param concatStr 拼接后的字符串
     * @param appSecret 应用秘钥
     * @return 添加秘钥后的字符串
     */
    public static String addSecret(String concatStr, String appSecret) {
        return appSecret + concatStr + appSecret;
    }
    
    /**
     * 第四步：MD5加密（静态方法）
     * @param text 待加密字符串
     * @return 32位MD5字符串
     */
    public static String md5(String text) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(text.getBytes());
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                sb.append(String.format("%02x", b & 0xff));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5加密失败", e);
        }
    }
    
    // ==================== 完整流程演示 ====================
    
    public static void main(String[] args) {
        // 示例参数
        String appKey = "123456";
        String appSecret = "abcdefg123";
        String body = "{\"order_id\":\"20170301000001\"}";
        String timestamp = "1488363493";
        String version = "1.0";
        
        System.out.println("=" * 60);
        System.out.println("签名生成示例");
        System.out.println("=" * 60);
        System.out.println("App Key: " + appKey);
        System.out.println("App Secret: " + appSecret);
        System.out.println("Body: " + body);
        System.out.println("Timestamp: " + timestamp);
        System.out.println("Version: " + version);
        System.out.println("-" * 60);
        
        // 创建签名生成器
        SignatureGenerator signer = new SignatureGenerator(appKey, appSecret);
        
        // 生成签名
        String signature = signer.generateSignature(body, timestamp, version);
        System.out.println("生成的签名: " + signature);
        System.out.println("签名长度: " + signature.length() + " 位");
        
        // 验证签名
        boolean isValid = signer.verifySignature(signature, body, timestamp, version);
        System.out.println("签名验证结果: " + (isValid ? "✓ 通过" : "✗ 失败"));
        
        System.out.println("\n" + "=" * 60);
        System.out.println("完整签名生成流程演示");
        System.out.println("=" * 60);
        
        // 第一步：构建参数并排序
        Map<String, String> params = new TreeMap<>();
        params.put("appKey", appKey);
        params.put("body", body);
        params.put("timestamp", timestamp);
        params.put("version", version);
        
        System.out.println("\n【第一步】构建参数并字典排序");
        System.out.println("原始参数: " + params);
        List<String> sortedKeys = sortParams(params);
        System.out.println("排序结果: " + String.join(" → ", sortedKeys));
        
        // 第二步：拼接参数
        System.out.println("\n【第二步】拼接key和value");
        String concatStr = concatParams(params, sortedKeys);
        System.out.println("拼接结果: " + concatStr);
        
        // 第三步：添加秘钥
        System.out.println("\n【第三步】首尾添加appSecret");
        String signStr = addSecret(concatStr, appSecret);
        System.out.println("签名字符串: " + signStr);
        
        // 第四步：MD5加密
        System.out.println("\n【第四步】MD5加密");
        String finalSignature = md5(signStr);
        System.out.println("最终签名: " + finalSignature);
        
        System.out.println("\n" + "=" * 60);
        
        // 示例2：自动生成时间戳
        System.out.println("\n自动生成时间戳示例:");
        String autoSignature = signer.generateSignature(body, "1.0");
        System.out.println("自动时间戳签名: " + autoSignature);
    }
}