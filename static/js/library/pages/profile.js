document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('change-password-form');
    const toast = document.getElementById('toast');

    function showToast(message, type = 'success') {
        toast.textContent = message;
        toast.className = `toast show toast-${type}`;
        
        setTimeout(() => {
            toast.className = 'toast';
        }, 3000);
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const old_password = document.getElementById('old_password').value;
        const new_password = document.getElementById('new_password').value;
        const confirm_password = document.getElementById('confirm_password').value;

        if (new_password !== confirm_password) {
            showToast('Mật khẩu mới không khớp!', 'error');
            return;
        }

        const submitBtn = form.querySelector('.btn-submit');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';

        try {
            const response = await fetch('/api/user/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    old_password,
                    new_password,
                    confirm_password
                })
            });

            const result = await response.json();

            if (response.ok) {
                showToast(result.message || 'Đổi mật khẩu thành công!');
                form.reset();
            } else {
                showToast(result.error || 'Có lỗi xảy ra!', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Lỗi kết nối server!', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
});
