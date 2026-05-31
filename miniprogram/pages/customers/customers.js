Page({
    data: {
        name: '',
        contact: '',
        address: '',
        customers: []
    },

    onLoad: function() {
        this.loadData();
    },

    onShow: function() {
        this.loadData();
    },

    loadData: function() {
        const customers = wx.getStorageSync('customers') || [];
        const records = wx.getStorageSync('records') || [];
        const result = customers.map(c => {
            let debt = 0;
            records.forEach(r => {
                if (r.customerId === c.id) {
                    debt += r.type === 'purchase' ? r.totalAmount : -r.totalAmount;
                }
            });
            return { ...c, debt: debt.toFixed(2) };
        });
        this.setData({ customers: result });
    },

    onNameInput: function(e) {
        this.setData({ name: e.detail.value });
    },

    onContactInput: function(e) {
        this.setData({ contact: e.detail.value });
    },

    onAddressInput: function(e) {
        this.setData({ address: e.detail.value });
    },

    addCustomer: function() {
        if (!this.data.name) {
            wx.showToast({ title: '请输入客户名称', icon: 'none' });
            return;
        }
        const customers = wx.getStorageSync('customers') || [];
        const newCustomer = {
            id: Date.now(),
            name: this.data.name,
            contact: this.data.contact,
            address: this.data.address
        };
        customers.push(newCustomer);
        wx.setStorageSync('customers', customers);
        wx.showToast({ title: '添加成功', icon: 'success' });
        this.setData({ name: '', contact: '', address: '' });
        this.loadData();
    }
});
