let cart = [];

document.getElementById('addItemForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const query = document.getElementById('searchQuery').value.trim();
    const qty = parseFloat(document.getElementById('itemQty').value);

    if (!query || isNaN(qty) || qty <= 0) return;

    fetch(`/api/product/find?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                addToCart(data, qty);
                document.getElementById('searchQuery').value = '';
                document.getElementById('itemQty').value = '1';
                document.getElementById('searchQuery').focus();
            } else {
                alert(data.error || "Product not found!");
            }
        })
        .catch(err => {
            console.error(err);
            alert("Network Error. Cannot fetch product.");
        });
});

function addToCart(product, qty) {
    // Check if product already exists in cart
    const existingIndex = cart.findIndex(item => item.product_id === product.id);
    if (existingIndex > -1) {
        cart[existingIndex].quantity += qty;
    } else {
        cart.push({
            product_id: product.id,
            name: product.name,
            price: product.price,
            price_type: product.price_type,
            gst_percent: product.gst_percent,
            quantity: qty
        });
    }
    renderCart();
}

function removeFromCart(index) {
    cart.splice(index, 1);
    renderCart();
}

function updateQty(index, newQty) {
    const qty = parseFloat(newQty);
    if (!isNaN(qty) && qty > 0) {
        cart[index].quantity = qty;
        renderCart();
    }
}

function renderCart() {
    const tbody = document.getElementById('cartTableBody');
    const emptyRow = document.getElementById('emptyCartRow');
    const generateBtn = document.getElementById('generateBillBtn');

    // Clear current items (except empty row if applicable)
    tbody.innerHTML = '';

    if (cart.length === 0) {
        tbody.appendChild(emptyRow);
        emptyRow.style.display = '';
        generateBtn.disabled = true;
        updateTotals();
        return;
    }

    generateBtn.disabled = false;

    cart.forEach((item, index) => {
        const subtotal = item.price * item.quantity;
        const gst = subtotal * (item.gst_percent / 100);
        const itemTotal = subtotal + gst;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <div class="fw-bold">${item.name}</div>
                <small class="text-muted">₹${item.price.toFixed(2)} / ${item.price_type}</small>
            </td>
            <td>₹${item.price.toFixed(2)}</td>
            <td style="width: 120px;">
                <input type="number" class="form-control form-control-sm" value="${item.quantity}" min="0.01" step="0.01" onchange="updateQty(${index}, this.value)">
            </td>
            <td>${item.gst_percent}% <br><small class="text-muted">(₹${gst.toFixed(2)})</small></td>
            <td class="fw-bold">₹${itemTotal.toFixed(2)}</td>
            <td>
                <button class="btn btn-sm btn-outline-danger" onclick="removeFromCart(${index})">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    updateTotals();
}

function updateTotals() {
    let subtotal = 0;
    let totalGst = 0;

    cart.forEach(item => {
        const itemSub = item.price * item.quantity;
        const itemGst = itemSub * (item.gst_percent / 100);
        subtotal += itemSub;
        totalGst += itemGst;
    });

    const discountInput = document.getElementById('discountAmt');
    let discount = parseFloat(discountInput.value) || 0;

    let grandTotal = subtotal + totalGst - discount;
    if (grandTotal < 0) grandTotal = 0;

    document.getElementById('subtotalAmt').innerText = '₹' + subtotal.toFixed(2);
    document.getElementById('gstAmt').innerText = '₹' + totalGst.toFixed(2);
    document.getElementById('grandTotalAmt').innerText = '₹' + grandTotal.toFixed(2);
}

document.getElementById('discountAmt').addEventListener('input', updateTotals);

document.getElementById('generateBillBtn').addEventListener('click', function () {
    if (cart.length === 0) return;

    this.disabled = true;
    this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';

    const payload = {
        payment_method: document.getElementById('paymentMethod').value,
        discount: parseFloat(document.getElementById('discountAmt').value) || 0,
        items: cart.map(item => ({
            product_id: item.product_id,
            quantity: item.quantity
        }))
    };

    fetch('/api/bill', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Redirect to invoice page
                window.location.href = `/invoice/${data.bill_id}`;
            } else {
                alert("Error creating bill: " + data.error);
                resetBtn();
            }
        })
        .catch(err => {
            console.error(err);
            alert("Network Error");
            resetBtn();
        });
});

function resetBtn() {
    const btn = document.getElementById('generateBillBtn');
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-printer-fill me-2"></i> Generate Bill & Print';
}
