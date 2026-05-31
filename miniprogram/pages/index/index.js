Page({
    data: {
        purchaseToday: 0,
        saleToday: 0,
        profitToday: 0,
        debts: []
    },
    
    onShow: function() {
        this.loadData();
    },
    
    loadData: function() {
        // 从本地存储获取今日数据
        const today = new Date().toISOString().split('T')[0];
        const records = wx.getStorageSync('records') || [];
        
        let purchaseToday = 0;
        let saleToday = 0;
        
        records.forEach(r => {
            if (r.date === today) {
                if (r.type === 'purchase') purchaseToday += r.amount;
                if (r.type === 'sale') saleToday += r.amount;
            }
        });
        
        // 计算欠款
        const customers = wx.getStorageSync('customers') || [];
        const debts = [];
        customers.forEach(c => {
            let debt = 0;
            records.forEach(r => {
                if (r.customerName === c.name) {
                    if (r.type === 'purchase') debt += r.amount;
                    if (r.type === 'sale') debt -= r.amount;
                }
            });
            if (debt !== 0) {
                debts.push({ name: c.name, debt: debt.toFixed(2) });
            }
        });
        
        this.setData({
            purchaseToday: purchaseToday.toFixed(2),
            saleToday: saleToday.toFixed(2),
            profitToday: (saleToday - purchaseToday).toFixed(2),
            debts: debts.slice(0, 5)
        });
    }
});
