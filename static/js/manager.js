let addProductModal;

document.addEventListener('DOMContentLoaded', () => {
    addProductModal = new bootstrap.Modal(document.getElementById('addProductModal'));
});

function editProduct(id, barcode, name, category, price, price_type, gst, stock) {
    document.getElementById('modalTitle').innerText = 'Edit Product';
    document.getElementById('prod_id').value = id;
    document.getElementById('prod_barcode').value = barcode;
    document.getElementById('prod_name').value = name;
    document.getElementById('prod_category').value = category;
    document.getElementById('prod_price').value = price;
    document.getElementById('prod_price_type').value = price_type;
    document.getElementById('prod_gst').value = gst;
    document.getElementById('prod_stock').value = stock;
    
    addProductModal.show();
}

function deleteProduct(id) {
    if(confirm('Are you sure you want to delete this product?')) {
        fetch(`/api/product/${id}`, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) location.reload();
            else alert('Error deleting product');
        });
    }
}

function saveProduct() {
    const id = document.getElementById('prod_id').value;
    const isEdit = id !== '';
    
    const data = {
        barcode: document.getElementById('prod_barcode').value,
        name: document.getElementById('prod_name').value,
        category: document.getElementById('prod_category').value,
        price: document.getElementById('prod_price').value,
        price_type: document.getElementById('prod_price_type').value,
        gst_percent: document.getElementById('prod_gst').value,
        stock: document.getElementById('prod_stock').value
    };
    
    // basic validation
    if(!data.name || !data.category || !data.price || !data.price_type) {
        alert("Please fill all required fields");
        return;
    }

    const url = isEdit ? `/api/product/${id}` : '/api/product';
    const method = isEdit ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        if(result.success) {
            location.reload();
        } else {
            alert('Error: ' + result.error);
        }
    })
    .catch(err => {
        console.error(err);
        alert("Network Error saving product.");
    });
}

// Reset modal when hidden
document.getElementById('addProductModal').addEventListener('hidden.bs.modal', function () {
    document.getElementById('productForm').reset();
    document.getElementById('prod_id').value = '';
    document.getElementById('modalTitle').innerText = 'Add New Product';
});
