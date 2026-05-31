App({
    onLaunch: function() {
        // 初始化预设商品
        if (!wx.getStorageSync('products')) {
            const products = require('./data/products.js');
            wx.setStorageSync('products', products);
        }
        
        // 初始化预设客户
        if (!wx.getStorageSync('customers')) {
            const customers = require('./data/customers.js');
            wx.setStorageSync('customers', customers);
        }
        
        // 初始化记录
        if (!wx.getStorageSync('records')) {
            wx.setStorageSync('records', []);
        }
    }
});
