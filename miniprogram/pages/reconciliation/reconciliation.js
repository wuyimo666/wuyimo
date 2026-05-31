Page({
    data: {
        customer: null,
        customers: [],
        purchases: [],
        sales: [],
        totalPurchase: 0,
        totalSale: 0,
        debt: 0
    },

    onLoad: function(options) {
        const customers = wx.getStorageSync('customers') || [];
        this.setData({ customers: customers });

        if (options.customerId) {
            this.loadCustomerData(options.customerId);
        }
    },

    onShow: function() {
        const customers = wx.getStorageSync('customers') || [];
        this.setData({ customers: customers });
    },

    loadCustomerData: function(customerId) {
        const customers = wx.getStorageSync('customers') || [];
        const records = wx.getStorageSync('records') || [];
        
        const customer = customers.find(c => c.id === customerId);
        if (!customer) return;

        const purchases = records.filter(r => r.type === 'purchase' && r.customerId === customerId)
            .sort((a, b) => a.date.localeCompare(b.date));
        const sales = records.filter(r => r.type === 'sale' && r.customerId === customerId)
            .sort((a, b) => a.date.localeCompare(b.date));

        const totalPurchase = purchases.reduce((sum, r) => sum + r.totalAmount, 0);
        const totalSale = sales.reduce((sum, r) => sum + r.totalAmount, 0);
        const debt = totalPurchase - totalSale;

        this.setData({
            customer: customer,
            purchases: purchases,
            sales: sales,
            totalPurchase: totalPurchase.toFixed(2),
            totalSale: totalSale.toFixed(2),
            debt: debt.toFixed(2)
        });
    },

    onCustomerChange: function(e) {
        const index = e.detail.value;
        const customer = this.data.customers[index];
        if (customer) {
            this.loadCustomerData(customer.id);
        }
    },

    printReconciliation: function() {
        wx.showToast({ title: '打印功能开发中...', icon: 'none' });
    },

    exportExcel: function() {
        wx.showToast({ title: '导出功能开发中...', icon: 'none' });
    }
});
