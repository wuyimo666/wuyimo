Page({
    data: {
        customers: [],
        products: [],
        customerIndex: -1,
        productIndex: -1,
        quantity: 1,
        unitPrice: 0,
        totalAmount: 0,
        recordDate: new Date().toISOString().split('T')[0],
        note: '',
        records: []
    },

    onLoad: function() {
        this.loadData();
    },

    onShow: function() {
        this.loadData();
    },

    loadData: function() {
        const customers = wx.getStorageSync('customers') || [];
        const products = wx.getStorageSync('products') || [];
        const records = wx.getStorageSync('records') || [];
        const purchaseRecords = records.filter(r => r.type === 'sale').sort((a, b) => b.date.localeCompare(a.date));
        
        this.setData({
            customers: customers,
            products: products,
            records: purchaseRecords.slice(0, 50)  // 只显示最近50条
        });
    },

    onCustomerChange: function(e) {
        this.setData({ customerIndex: e.detail.value });
    },

    onProductChange: function(e) {
        const index = e.detail.value;
        const product = this.data.products[index];
        this.setData({
            productIndex: index,
            unitPrice: product.defaultPrice || 0
        });
        this.calcTotal();
    },

    onQuantityInput: function(e) {
        this.setData({ quantity: parseFloat(e.detail.value) || 0 });
        this.calcTotal();
    },

    onUnitPriceInput: function(e) {
        this.setData({ unitPrice: parseFloat(e.detail.value) || 0 });
        this.calcTotal();
    },

    onDateChange: function(e) {
        this.setData({ recordDate: e.detail.value });
    },

    onNoteInput: function(e) {
        this.setData({ note: e.detail.value });
    },

    calcTotal: function() {
        const total = (this.data.quantity || 0) * (this.data.unitPrice || 0);
        this.setData({ totalAmount: total.toFixed(2) });
    },

    saveRecord: function() {
        if (this.data.customerIndex < 0) {
            wx.showToast({ title: '请选择供应商', icon: 'none' });
            return;
        }
        if (this.data.productIndex < 0) {
            wx.showToast({ title: '请选择商品', icon: 'none' });
            return;
        }

        const record = {
            id: Date.now(),
            type: 'sale',
            customerId: this.data.customers[this.data.customerIndex].id,
            customerName: this.data.customers[this.data.customerIndex].name,
            productId: this.data.products[this.data.productIndex].id,
            productName: this.data.products[this.data.productIndex].name,
            quantity: this.data.quantity,
            unitPrice: this.data.unitPrice,
            totalAmount: parseFloat(this.data.totalAmount),
            date: this.data.recordDate,
            note: this.data.note,
            createTime: new Date().toISOString()
        };

        const records = wx.getStorageSync('records') || [];
        records.push(record);
        wx.setStorageSync('records', records);

        wx.showToast({ title: '保存成功', icon: 'success' });

        // 清空表单
        this.setData({
            customerIndex: -1,
            productIndex: -1,
            quantity: 1,
            unitPrice: 0,
            totalAmount: 0,
            note: '',
            records: [...records.filter(r => r.type === 'sale').sort((a, b) => b.date.localeCompare(a.date)).slice(0, 50)]
        });
    }
});
