# e:/projects/python/django/teguh/babycare/core/views.py
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, View, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.db.models import Sum, Q
from django.db import OperationalError
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta

from .models import Pasien, Registrasi, Pemasukan, Pengeluaran, Notifikasi, Terapis, JenisTerapi, Cabang, User
from .forms import RegistrasiForm, PemasukanForm, PengeluaranForm


def format_rupiah(value):
    """Format number as Indonesian Rupiah currency."""
    try:
        if isinstance(value, str):
            value = int(float(value))
        else:
            value = int(value)
        formatted = "{:,}".format(value).replace(",", ".")
        return f"Rp {formatted}"
    except (ValueError, TypeError):
        return "Rp 0"


class HealthCheckView(View):
    """Simple health check endpoint."""
    def get(self, request):
        return HttpResponse("OK")


class DebugView(View):
    """Debug endpoint to check auth state."""
    def get(self, request):
        return HttpResponse(f"authenticated={request.user.is_authenticated}, user={request.user}")


class IndexView(View):
    """Redirect to login if not authenticated, dashboard if authenticated."""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return redirect('custom_login')


class SimpleLoginView(FormView):
    """Simple custom login view for debugging."""
    template_name = 'core/simple_login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Return form with errors
        return self.render_to_response(self.get_context_data(form=form))


class DashboardView(LoginRequiredMixin, View):
    """Simple dashboard view."""
    login_url = '/login/'
    
    def get(self, request):
        from django.shortcuts import render
        from django.utils import timezone
        from datetime import datetime, timedelta
        from django.db.models import Sum, Count, Q
        import json
        
        today = timezone.now().date()
        current_month_start = today.replace(day=1)
        
        # Calculate statistics
        total_pasien = Pasien.objects.count()
        registrasi_hari_ini = Registrasi.objects.filter(tanggal_kunjungan=today).count()
        pendapatan_bulan_ini = Pemasukan.objects.filter(
            tanggal__year=today.year,
            tanggal__month=today.month
        ).aggregate(total=Sum('jumlah'))['total'] or 0
        notifikasi_belum_dibaca = Notifikasi.objects.filter(sudah_dibaca=False).count()
        
        # Chart Data 1: Registrasi per bulan (last 12 months)
        registrasi_per_bulan = []
        labels_bulan = []
        for i in range(11, -1, -1):
            month_date = today - timedelta(days=30*i)
            month_start = month_date.replace(day=1)
            if i > 0:
                month_end = (month_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            else:
                month_end = today
            
            count = Registrasi.objects.filter(
                tanggal_kunjungan__gte=month_start,
                tanggal_kunjungan__lte=month_end
            ).count()
            registrasi_per_bulan.append(count)
            labels_bulan.append(month_date.strftime('%b'))
        
        # Chart Data 2: Top Terapis (by number of sessions)
        top_terapis = Registrasi.objects.values('terapis__nama_terapis').annotate(
            count=Count('id')
        ).order_by('-count')[:8]
        terapis_names = [t['terapis__nama_terapis'] or 'Unknown' for t in top_terapis]
        terapis_counts = [t['count'] for t in top_terapis]
        
        # Chart Data 3: Jenis Terapi (by frequency)
        jenis_terapi_data = Registrasi.objects.values('jenis_terapi__nama_terapi').annotate(
            count=Count('id')
        ).order_by('-count')[:8]
        terapi_names = [t['jenis_terapi__nama_terapi'] for t in jenis_terapi_data]
        terapi_counts = [t['count'] for t in jenis_terapi_data]
        
        # Chart Data 4: Pemasukan vs Pengeluaran (current month)
        pemasukan_bulan = Pemasukan.objects.filter(
            tanggal__year=today.year,
            tanggal__month=today.month
        ).aggregate(total=Sum('jumlah'))['total'] or 0
        
        pengeluaran_bulan = Pengeluaran.objects.filter(
            tanggal__year=today.year,
            tanggal__month=today.month
        ).aggregate(total=Sum('jumlah'))['total'] or 0
        
        # Chart Data 5: Pasien per cabang
        pasien_per_cabang = Pasien.objects.values('cabang__nama_cabang').annotate(
            count=Count('id')
        ).order_by('-count')
        cabang_names = [p['cabang__nama_cabang'] or 'Tanpa Cabang' for p in pasien_per_cabang]
        cabang_counts = [p['count'] for p in pasien_per_cabang]
        
        # Chart Data 6: Daily registrations trend (last 30 days)
        daily_registrasi = []
        labels_hari = []
        for i in range(29, -1, -1):
            day = today - timedelta(days=i)
            count = Registrasi.objects.filter(tanggal_kunjungan=day).count()
            daily_registrasi.append(count)
            labels_hari.append(day.strftime('%d'))
        
        context = {
            'username': request.user.username,
            'fullname': getattr(request.user, 'full_name', 'N/A'),
            'is_authenticated': request.user.is_authenticated,
            'total_pasien': total_pasien,
            'registrasi_hari_ini': registrasi_hari_ini,
            'pendapatan_bulan_ini': pendapatan_bulan_ini,
            'notifikasi_belum_dibaca': notifikasi_belum_dibaca,
            # Chart data
            'registrasi_per_bulan': json.dumps(registrasi_per_bulan),
            'labels_bulan': json.dumps(labels_bulan),
            'terapis_names': json.dumps(terapis_names),
            'terapis_counts': json.dumps(terapis_counts),
            'terapi_names': json.dumps(terapi_names),
            'terapi_counts': json.dumps(terapi_counts),
            'pemasukan_bulan': float(pemasukan_bulan),
            'pengeluaran_bulan': float(pengeluaran_bulan),
            'cabang_names': json.dumps(cabang_names),
            'cabang_counts': json.dumps(cabang_counts),
            'daily_registrasi': json.dumps(daily_registrasi),
            'labels_hari': json.dumps(labels_hari),
        }
        return render(request, 'core/dashboard.html', context)

class RegistrasiListView(LoginRequiredMixin, ListView):
    model = Registrasi
    template_name = 'core/registrasi_list.html'
    context_object_name = 'registrasis'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            'pasien', 'jenis_terapi', 'terapis', 'cabang'
        ).order_by('-tanggal_kunjungan')
        
        # Add annotation for outstanding balance
        from django.db.models import Sum, F, DecimalField, Case, When
        from decimal import Decimal
        qs = qs.annotate(
            total_paid=Sum('pemasukan__jumlah', output_field=DecimalField())
        )
        # Calculate remaining balance as total_bayar - total_paid (default 0 if null)
        qs = qs.annotate(
            sisa_tagihan=Case(
                When(total_paid__isnull=True, then=F('total_bayar')),
                default=F('total_bayar') - F('total_paid'),
                output_field=DecimalField()
            )
        )
        
        user_roles = getattr(self.request, 'user_roles', set())
        if 'terapis' in user_roles:
            qs = qs.filter(terapis__user=self.request.user)
        else:
            if getattr(self.request, 'cabang_id', None) is not None:
                qs = qs.filter(cabang_id=self.request.cabang_id)
        
        # Apply filters from GET parameters
        # Filter by date range
        tanggal_dari = self.request.GET.get('tanggal_dari')
        tanggal_sampai = self.request.GET.get('tanggal_sampai')
        
        if tanggal_dari:
            try:
                from datetime import datetime
                tanggal_dari_date = datetime.strptime(tanggal_dari, '%Y-%m-%d').date()
                qs = qs.filter(tanggal_kunjungan__gte=tanggal_dari_date)
            except:
                pass
        
        if tanggal_sampai:
            try:
                from datetime import datetime
                tanggal_sampai_date = datetime.strptime(tanggal_sampai, '%Y-%m-%d').date()
                qs = qs.filter(tanggal_kunjungan__lte=tanggal_sampai_date)
            except:
                pass
        
        # Filter by pasien (nama_anak)
        pasien_query = self.request.GET.get('pasien_query')
        if pasien_query:
            qs = qs.filter(pasien__nama_anak__icontains=pasien_query)
        
        # Filter by jenis_terapi
        jenis_terapi_id = self.request.GET.get('jenis_terapi_id')
        if jenis_terapi_id:
            qs = qs.filter(jenis_terapi_id=jenis_terapi_id)
        
        # Filter by terapis
        terapis_id = self.request.GET.get('terapis_id')
        if terapis_id:
            qs = qs.filter(terapis_id=terapis_id)
        
        # Filter by kode_registrasi
        kode_registrasi = self.request.GET.get('kode_registrasi')
        if kode_registrasi:
            qs = qs.filter(kode_registrasi__icontains=kode_registrasi)
        
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter values
        context['tanggal_dari'] = self.request.GET.get('tanggal_dari', '')
        context['tanggal_sampai'] = self.request.GET.get('tanggal_sampai', '')
        context['pasien_query'] = self.request.GET.get('pasien_query', '')
        context['jenis_terapi_id'] = self.request.GET.get('jenis_terapi_id', '')
        context['terapis_id'] = self.request.GET.get('terapis_id', '')
        context['kode_registrasi'] = self.request.GET.get('kode_registrasi', '')
        
        # Get filter options
        from core.models import JenisTerapi, Terapis
        context['jenis_terapi_list'] = JenisTerapi.objects.all()
        context['terapis_list'] = Terapis.objects.all()
        
        return context

class RegistrasiCreateView(LoginRequiredMixin, CreateView):
    model = Registrasi
    form_class = RegistrasiForm
    template_name = 'core/registrasi_form.html'
    success_url = reverse_lazy('dashboard')

    def get_initial(self):
        """Set default values for form fields."""
        initial = super().get_initial()
        from datetime import date
        initial['tanggal_kunjungan'] = date.today()
        return initial

    def form_valid(self, form):
        """Generate kode_registrasi before saving"""
        from datetime import date
        
        # Auto-generate kode_registrasi if not provided
        if not form.instance.kode_registrasi:
            today = date.today()
            cabang_id = form.instance.cabang_id
            
            # Format: P + CABANG_ID(2digit) + MMYY + sequential number (3 digits)
            # Example: P010326001 (P=prefix, 01=cabang_id, 03=March, 26=2026, 001=first record)
            # If no cabang: P000326001
            cabang_code = f'{cabang_id:02d}' if cabang_id else '00'
            month_year = today.strftime('%m%y')
            prefix = f'P{cabang_code}{month_year}'
            
            # Get the highest sequence number for this cabang/month/year
            last_registrasi = Registrasi.objects.filter(
                kode_registrasi__startswith=prefix,
                cabang_id=cabang_id
            ).order_by('-kode_registrasi', '-id').first()
            
            if last_registrasi and last_registrasi.kode_registrasi:
                try:
                    # Extract the sequence number from the last kode
                    last_seq = int(last_registrasi.kode_registrasi[-3:])
                    next_seq = last_seq + 1
                except (ValueError, IndexError):
                    next_seq = 1
            else:
                next_seq = 1
            
            # Generate the new kode
            form.instance.kode_registrasi = f'{prefix}{next_seq:03d}'
        
        messages.success(self.request, 'Data registrasi berhasil disimpan!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Debug: print form errors to console
        print("Form errors:", form.errors)
        print("Form cleaned_data:", getattr(form, 'cleaned_data', 'No cleaned data'))
        
        # Create detailed error message
        error_messages = []
        for field, errors in form.errors.items():
            if field == '__all__':
                error_messages.extend(errors)
            else:
                field_label = form.fields[field].label or field
                for error in errors:
                    error_messages.append(f"{field_label}: {error}")
        
        if error_messages:
            messages.error(self.request, 'Terjadi kesalahan:<br>' + '<br>'.join(error_messages))
        else:
            messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        
        return super().form_invalid(form)

class RegistrasiEditView(LoginRequiredMixin, UpdateView):
    model = Registrasi
    form_class = RegistrasiForm
    template_name = 'core/registrasi_form.html'
    success_url = reverse_lazy('registrasi_list')

    def form_valid(self, form):
        messages.success(self.request, 'Data registrasi berhasil diupdate!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Create detailed error message
        error_messages = []
        for field, errors in form.errors.items():
            if field == '__all__':
                error_messages.extend(errors)
            else:
                field_label = form.fields[field].label or field
                for error in errors:
                    error_messages.append(f"{field_label}: {error}")
        
        if error_messages:
            messages.error(self.request, 'Terjadi kesalahan:<br>' + '<br>'.join(error_messages))
        else:
            messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        
        return super().form_invalid(form)

class PemasukanCreateView(LoginRequiredMixin, CreateView):
    model = Pemasukan
    form_class = PemasukanForm
    template_name = 'core/pemasukan_form.html'
    success_url = reverse_lazy('pemasukan_list')

    def get_success_url(self):
        """Check if there's a 'next' parameter and use it, otherwise use default."""
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return next_url
        return self.success_url

    def get_initial(self):
        """Set default values for form fields."""
        initial = super().get_initial()
        from datetime import date
        initial['tanggal'] = date.today()
        return initial

    def get_form(self, form_class=None):
        """Override to filter registrasi queryset - only show unpaid/partially paid registrations."""
        form = super().get_form(form_class)
        
        # Get all registrasi IDs with their total payments
        from django.db.models import Sum, Q
        paid_registrasi = Pemasukan.objects.values('registrasi_id').annotate(
            total_paid=Sum('jumlah')
        )
        
        # Build dict of registrasi_id -> total_paid
        paid_dict = {item['registrasi_id']: item['total_paid'] for item in paid_registrasi if item['registrasi_id']}
        
        # Filter registrasi: exclude fully paid ones
        unpaid_registrasi = []
        for reg in Registrasi.objects.filter(is_deleted=False).select_related('pasien', 'jenis_terapi', 'terapis'):
            total_paid = paid_dict.get(reg.id, 0) or 0
            total_bayar = reg.total_bayar or 0
            
            # Include if not fully paid
            if total_paid < total_bayar:
                unpaid_registrasi.append(reg.id)
        
        # Update form queryset
        form.fields['registrasi'].queryset = Registrasi.objects.filter(
            id__in=unpaid_registrasi
        ).select_related('pasien', 'jenis_terapi', 'terapis').order_by('-tanggal_kunjungan')
        
        return form

    def form_valid(self, form):
        try:
            obj = form.save(commit=False)
            if obj is None:
                print("ERROR: form.save(commit=False) returned None!")
                messages.error(self.request, 'Terjadi kesalahan saat menyimpan data.')
                return self.form_invalid(form)
            obj.created_by = self.request.user
            obj.save()
            self.object = obj  # IMPORTANT: Set self.object for get_success_url()
            
            # Create success message with kembalian info if applicable
            msg = '✅ Pembayaran berhasil disimpan!'
            if obj.jumlah_bayar and obj.jumlah and obj.jumlah_bayar > obj.jumlah:
                kembalian = obj.jumlah_bayar - obj.jumlah
                msg += f' Kembalian: Rp {kembalian:,.0f}'.replace(',', '.')
            
            messages.success(self.request, msg)
            return redirect(self.get_success_url())
        except AttributeError as e:
            print(f"AttributeError in form_valid: {e}")
            print(f"form.save() returned: {form.save(commit=False) if hasattr(form, 'save') else 'No save method'}")
            messages.error(self.request, f'Terjadi kesalahan teknis: {str(e)}')
            return self.form_invalid(form)
        except Exception as e:
            print(f"Exception in form_valid: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            messages.error(self.request, f'Terjadi kesalahan: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        # Debug: print form errors to console
        print("Form errors:", form.errors)
        print("Form cleaned_data:", getattr(form, 'cleaned_data', 'No cleaned data'))
        
        # Create detailed error message
        error_messages = []
        for field, errors in form.errors.items():
            if field == '__all__':
                error_messages.extend(errors)
            else:
                field_label = form.fields[field].label or field
                for error in errors:
                    error_messages.append(f"{field_label}: {error}")
        
        if error_messages:
            messages.error(self.request, 'Terjadi kesalahan:<br>' + '<br>'.join(error_messages))
        else:
            messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        
        return super().form_invalid(form)


class PemasukanListView(LoginRequiredMixin, ListView):
    model = Pemasukan
    template_name = 'core/pemasukan_list.html'
    context_object_name = 'pemasukans'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('registrasi__pasien', 'registrasi__jenis_terapi', 'cabang').order_by('-tanggal', '-created_at')
        if getattr(self.request, 'cabang_id', None) is not None:
            qs = qs.filter(cabang_id=self.request.cabang_id)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Sum
        # Calculate total from all records (not just current page)
        qs = self.get_queryset()
        total = qs.aggregate(total=Sum('jumlah'))['total'] or 0
        context['total_pemasukan'] = total
        return context


class PemasukanEditView(LoginRequiredMixin, UpdateView):
    model = Pemasukan
    form_class = PemasukanForm
    template_name = 'core/pemasukan_form.html'
    success_url = reverse_lazy('pemasukan_list')

    def get_form(self, form_class=None):
        """Override to filter registrasi queryset - only show unpaid/partially paid registrations."""
        form = super().get_form(form_class)
        
        # Get all registrasi IDs with their total payments (excluding current pemasukan being edited)
        from django.db.models import Sum, Q
        paid_registrasi = Pemasukan.objects.exclude(pk=self.object.pk).values('registrasi_id').annotate(
            total_paid=Sum('jumlah')
        )
        
        # Build dict of registrasi_id -> total_paid
        paid_dict = {item['registrasi_id']: item['total_paid'] for item in paid_registrasi if item['registrasi_id']}
        
        # Filter registrasi: exclude fully paid ones
        unpaid_registrasi = []
        for reg in Registrasi.objects.filter(is_deleted=False).select_related('pasien', 'jenis_terapi', 'terapis'):
            total_paid = paid_dict.get(reg.id, 0) or 0
            total_bayar = reg.total_bayar or 0
            
            # Include if not fully paid OR if it's the current pemasukan's registrasi
            if total_paid < total_bayar or reg.id == (self.object.registrasi_id if self.object.registrasi else None):
                unpaid_registrasi.append(reg.id)
        
        # Update form queryset
        form.fields['registrasi'].queryset = Registrasi.objects.filter(
            id__in=unpaid_registrasi
        ).select_related('pasien', 'jenis_terapi', 'terapis').order_by('-tanggal_kunjungan')
        
        return form

    def form_valid(self, form):
        obj = form.save()
        
        # Create success message with kembalian info if applicable
        msg = '✅ Data pembayaran berhasil diupdate!'
        if obj.jumlah_bayar and obj.jumlah and obj.jumlah_bayar > obj.jumlah:
            kembalian = obj.jumlah_bayar - obj.jumlah
            msg += f' Kembalian: Rp {kembalian:,.0f}'.replace(',', '.')
        
        messages.success(self.request, msg)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        error_messages = []
        for field, errors in form.errors.items():
            if field == '__all__':
                error_messages.extend(errors)
            else:
                field_label = form.fields[field].label or field
                for error in errors:
                    error_messages.append(f"{field_label}: {error}")
        
        if error_messages:
            messages.error(self.request, 'Terjadi kesalahan:<br>' + '<br>'.join(error_messages))
        else:
            messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        
        return super().form_invalid(form)


class PengeluaranListView(LoginRequiredMixin, ListView):
    model = Pengeluaran
    template_name = 'core/pengeluaran_list.html'
    context_object_name = 'pengeluarans'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().order_by('-tanggal', '-created_at')
        if getattr(self.request, 'cabang_id', None) is not None:
            qs = qs.filter(cabang_id=self.request.cabang_id)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Sum
        # Calculate total from all records (not just current page)
        qs = self.get_queryset()
        total = qs.aggregate(total=Sum('jumlah'))['total'] or 0
        context['total_pengeluaran'] = total
        return context


class PengeluaranCreateView(LoginRequiredMixin, CreateView):
    model = Pengeluaran
    form_class = PengeluaranForm
    template_name = 'core/pengeluaran_form.html'
    success_url = reverse_lazy('dashboard')

    def get_initial(self):
        """Set default values for form fields."""
        initial = super().get_initial()
        from datetime import date
        initial['tanggal'] = date.today()
        return initial

    def form_valid(self, form):
        try:
            obj = form.save(commit=False)
            if obj is None:
                print("ERROR: form.save(commit=False) returned None!")
                messages.error(self.request, 'Terjadi kesalahan saat menyimpan data.')
                return self.form_invalid(form)
            obj.created_by = self.request.user
            obj.save()
            self.object = obj
            messages.success(self.request, 'Data pengeluaran berhasil disimpan!')
            return redirect(self.get_success_url())
        except Exception as e:
            print(f"Exception in form_valid: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            messages.error(self.request, f'Terjadi kesalahan: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        # Debug: print form errors to console
        print("Form errors:", form.errors)
        print("Form cleaned_data:", getattr(form, 'cleaned_data', 'No cleaned data'))
        
        # Create detailed error message
        error_messages = []
        for field, errors in form.errors.items():
            if field == '__all__':
                error_messages.extend(errors)
            else:
                field_label = form.fields[field].label or field
                for error in errors:
                    error_messages.append(f"{field_label}: {error}")
        
        if error_messages:
            messages.error(self.request, 'Terjadi kesalahan:<br>' + '<br>'.join(error_messages))
        else:
            messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        
        return super().form_invalid(form)


class PengeluaranEditView(LoginRequiredMixin, UpdateView):
    model = Pengeluaran
    form_class = PengeluaranForm
    template_name = 'core/pengeluaran_form.html'
    success_url = reverse_lazy('pengeluaran_list')

    def form_valid(self, form):
        obj = form.save()
        messages.success(self.request, '✅ Data pengeluaran berhasil diupdate!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        error_messages = []
        for field, errors in form.errors.items():
            if field == '__all__':
                error_messages.extend(errors)
            else:
                field_label = form.fields[field].label or field
                for error in errors:
                    error_messages.append(f"{field_label}: {error}")
        
        if error_messages:
            messages.error(self.request, 'Terjadi kesalahan:<br>' + '<br>'.join(error_messages))
        else:
            messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        
        return super().form_invalid(form)


# Master Data Views
from .models import Pasien, JenisTerapi, Terapis

class PasienListView(LoginRequiredMixin, ListView):
    """List all pasien."""
    model = Pasien
    template_name = 'core/pasien_list.html'
    context_object_name = 'pasiens'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        if getattr(self.request, 'cabang_id', None) is not None:
            qs = qs.filter(cabang_id=self.request.cabang_id)
        return qs

class PasienCreateView(LoginRequiredMixin, CreateView):
    """Create new pasien."""
    model = Pasien
    fields = ['nama_anak', 'tanggal_lahir', 'jenis_kelamin', 'nama_orang_tua', 'alamat', 'no_wa', 'cabang']
    template_name = 'core/pasien_form.html'
    success_url = reverse_lazy('pasien_list')
    
    def get_form(self, form_class=None):
        from django import forms
        form = super().get_form(form_class)
        form.fields['nama_anak'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama anak'})
        form.fields['tanggal_lahir'].widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        form.fields['jenis_kelamin'].widget = forms.Select(
            choices=[('', '-- Pilih --'), ('L', 'Laki-laki'), ('P', 'Perempuan')],
            attrs={'class': 'form-select'}
        )
        form.fields['nama_orang_tua'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama orang tua'})
        form.fields['alamat'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat lengkap'})
        form.fields['no_wa'].widget.attrs.update({'class': 'form-control', 'placeholder': '08xx-xxxx-xxxx'})
        form.fields['cabang'].widget.attrs.update({'class': 'form-select'})
        return form
    
    def form_valid(self, form):
        # Auto-generate kode_pasien
        if not form.instance.kode_pasien:
            from django.db.models import Max
            last_pasien = Pasien.objects.aggregate(Max('id'))['id__max']
            next_id = (last_pasien or 0) + 1
            form.instance.kode_pasien = f'P{next_id:04d}'
        messages.success(self.request, f'Data pasien {form.instance.nama_anak} berhasil disimpan dengan kode {form.instance.kode_pasien}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        return super().form_invalid(form)

class PasienEditView(LoginRequiredMixin, UpdateView):
    """Edit existing pasien."""
    model = Pasien
    fields = ['nama_anak', 'tanggal_lahir', 'jenis_kelamin', 'nama_orang_tua', 'alamat', 'no_wa', 'cabang']
    template_name = 'core/pasien_form.html'
    context_object_name = 'object'
    pk_url_kwarg = 'pk'
    
    def get_success_url(self):
        return reverse_lazy('pasien_list')
    
    def get_form(self, form_class=None):
        from django import forms
        form = super().get_form(form_class)
        form.fields['nama_anak'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama anak'})
        form.fields['tanggal_lahir'].widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        form.fields['jenis_kelamin'].widget = forms.Select(
            choices=[('', '-- Pilih --'), ('L', 'Laki-laki'), ('P', 'Perempuan')],
            attrs={'class': 'form-select'}
        )
        form.fields['nama_orang_tua'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama orang tua'})
        form.fields['alamat'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat lengkap'})
        form.fields['no_wa'].widget.attrs.update({'class': 'form-control', 'placeholder': '08xx-xxxx-xxxx'})
        form.fields['cabang'].widget.attrs.update({'class': 'form-select'})
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f'Data pasien {form.instance.nama_anak} berhasil diperbarui!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        return super().form_invalid(form)

class TerapisListView(LoginRequiredMixin, ListView):
    """List all terapis."""
    model = Terapis
    template_name = 'core/terapis_list.html'
    context_object_name = 'terapis_list'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        if getattr(self.request, 'cabang_id', None) is not None:
            qs = qs.filter(cabang_id=self.request.cabang_id)
        return qs

class TerapisCreateView(LoginRequiredMixin, CreateView):
    """Create new terapis."""
    model = Terapis
    fields = ['nama_terapis', 'no_hp', 'alamat', 'cabang', 'biaya_transport_default', 'is_active']
    template_name = 'core/terapis_form.html'
    success_url = reverse_lazy('terapis_list')
    
    def get_form(self, form_class=None):
        from django import forms
        form = super().get_form(form_class)
        form.fields['nama_terapis'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama terapis'})
        form.fields['no_hp'].widget.attrs.update({'class': 'form-control', 'placeholder': '08xx-xxxx-xxxx'})
        form.fields['alamat'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat lengkap'})
        form.fields['cabang'].widget.attrs.update({'class': 'form-select'})
        form.fields['biaya_transport_default'].widget.attrs.update({'class': 'form-control', 'placeholder': '0'})
        form.fields['is_active'].widget.attrs.update({'class': 'form-check-input', 'checked': 'checked'})
        form.fields['is_active'].initial = True
        form.fields['biaya_transport_default'].initial = 0
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f'Data terapis {form.instance.nama_terapis} berhasil disimpan!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        return super().form_invalid(form)

class TerapisUpdateView(LoginRequiredMixin, UpdateView):
    """Update terapis."""
    model = Terapis
    fields = ['nama_terapis', 'no_hp', 'alamat', 'cabang', 'biaya_transport_default', 'is_active']
    template_name = 'core/terapis_form.html'
    success_url = reverse_lazy('terapis_list')
    
    def get_form(self, form_class=None):
        from django import forms
        form = super().get_form(form_class)
        form.fields['nama_terapis'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama terapis'})
        form.fields['no_hp'].widget.attrs.update({'class': 'form-control', 'placeholder': '08xx-xxxx-xxxx'})
        form.fields['alamat'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat lengkap'})
        form.fields['cabang'].widget.attrs.update({'class': 'form-select'})
        form.fields['biaya_transport_default'].widget.attrs.update({'class': 'form-control', 'placeholder': '0'})
        form.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f'Data terapis {form.instance.nama_terapis} berhasil diperbarui!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        return super().form_invalid(form)

class TerapisDeleteView(LoginRequiredMixin, DeleteView):
    """Delete terapis."""
    model = Terapis
    success_url = reverse_lazy('terapis_list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        nama = obj.nama_terapis
        messages.success(request, f'Data terapis {nama} berhasil dihapus!')
        return super().delete(request, *args, **kwargs)

class JenisTerapiListView(LoginRequiredMixin, ListView):
    """List all jenis terapi."""
    model = JenisTerapi
    template_name = 'core/jenis_terapi_list.html'
    context_object_name = 'jenis_terapi_list'
    paginate_by = 25

class JenisTerapiCreateView(LoginRequiredMixin, CreateView):
    """Create new jenis terapi."""
    model = JenisTerapi
    fields = ['nama_terapi', 'kategori_usia_min', 'kategori_usia_max', 'harga']
    template_name = 'core/jenis_terapi_form.html'
    success_url = reverse_lazy('jenis_terapi_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['nama_terapi'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama jenis terapi'})
        form.fields['kategori_usia_min'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Min. umur (bulan)'})
        form.fields['kategori_usia_max'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Max. umur (bulan)'})
        form.fields['harga'].widget.attrs.update({'class': 'form-control', 'placeholder': '0'})
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f'Jenis terapi {form.instance.nama_terapi} berhasil disimpan!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        return super().form_invalid(form)

class JenisTerapiUpdateView(LoginRequiredMixin, UpdateView):
    """Update jenis terapi."""
    model = JenisTerapi
    fields = ['nama_terapi', 'kategori_usia_min', 'kategori_usia_max', 'harga']
    template_name = 'core/jenis_terapi_form.html'
    success_url = reverse_lazy('jenis_terapi_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['nama_terapi'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama jenis terapi'})
        form.fields['kategori_usia_min'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Min. umur (bulan)'})
        form.fields['kategori_usia_max'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Max. umur (bulan)'})
        form.fields['harga'].widget.attrs.update({'class': 'form-control', 'placeholder': '0'})
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f'Jenis terapi {form.instance.nama_terapi} berhasil diperbarui!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        return super().form_invalid(form)

class JenisTerapiDeleteView(LoginRequiredMixin, DeleteView):
    """Delete jenis terapi."""
    model = JenisTerapi
    success_url = reverse_lazy('jenis_terapi_list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        nama = obj.nama_terapi
        messages.success(request, f'Jenis terapi {nama} berhasil dihapus!')
        return super().delete(request, *args, **kwargs)

class CabangListView(LoginRequiredMixin, ListView):
    """List all cabang."""
    model = Cabang
    template_name = 'core/cabang_list.html'
    context_object_name = 'cabang_list'
    paginate_by = 25

class CabangCreateView(LoginRequiredMixin, CreateView):
    """Create new cabang."""
    model = Cabang
    fields = ['nama_cabang', 'alamat']
    template_name = 'core/cabang_form.html'
    success_url = reverse_lazy('cabang_list')
    
    def get_form(self, form_class=None):
        from django import forms
        form = super().get_form(form_class)
        form.fields['nama_cabang'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama cabang'})
        form.fields['alamat'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat lengkap'})
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f'Cabang {form.instance.nama_cabang} berhasil disimpan!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        return super().form_invalid(form)

class CabangUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing cabang."""
    model = Cabang
    fields = ['nama_cabang', 'alamat']
    template_name = 'core/cabang_form.html'
    success_url = reverse_lazy('cabang_list')
    
    def get_form(self, form_class=None):
        from django import forms
        form = super().get_form(form_class)
        form.fields['nama_cabang'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama cabang'})
        form.fields['alamat'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat lengkap'})
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f'Cabang {form.instance.nama_cabang} berhasil diperbarui!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        return super().form_invalid(form)

class CabangDeleteView(LoginRequiredMixin, DeleteView):
    """Delete existing cabang."""
    model = Cabang
    success_url = reverse_lazy('cabang_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nama_cabang = self.object.nama_cabang
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, f'Cabang {nama_cabang} berhasil dihapus!')
        return response


class RekapTindakanListView(LoginRequiredMixin, ListView):
    """Rekap tindakan with filtering"""
    model = Registrasi
    template_name = 'core/rekap_tindakan_list.html'
    context_object_name = 'rekap_list'
    paginate_by = 50

    def get_queryset(self):
        today = timezone.now().date()
        qs = Registrasi.objects.select_related(
            'pasien', 'jenis_terapi', 'terapis', 'cabang'
        ).order_by('-tanggal_kunjungan')
        
        period = self.request.GET.get('period', 'harian')
        
        if period == 'harian':
            qs = qs.filter(tanggal_kunjungan=today)
        elif period == 'minggu':
            start_date = today - timedelta(days=6)
            qs = qs.filter(tanggal_kunjungan__gte=start_date, tanggal_kunjungan__lte=today)
        elif period == '3bulan':
            start_date = today - timedelta(days=89)
            qs = qs.filter(tanggal_kunjungan__gte=start_date, tanggal_kunjungan__lte=today)
        elif period == '6bulan':
            start_date = today - timedelta(days=179)
            qs = qs.filter(tanggal_kunjungan__gte=start_date, tanggal_kunjungan__lte=today)
        elif period == '1tahun':
            start_date = today - timedelta(days=364)
            qs = qs.filter(tanggal_kunjungan__gte=start_date, tanggal_kunjungan__lte=today)
        
        # Custom date range if provided
        start_custom = self.request.GET.get('start_date')
        end_custom = self.request.GET.get('end_date')
        if start_custom and end_custom:
            try:
                start_date = datetime.strptime(start_custom, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_custom, '%Y-%m-%d').date()
                qs = qs.filter(tanggal_kunjungan__gte=start_date, tanggal_kunjungan__lte=end_date)
            except ValueError:
                pass
        
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get same queryset for totals (all records, not just current page)
        qs = self.get_queryset()
        
        # Calculate totals
        total_harga = qs.aggregate(total=Sum('harga'))['total'] or 0
        total_transport = qs.aggregate(total=Sum('biaya_transport'))['total'] or 0
        total_pendapatan = qs.aggregate(total=Sum('total_bayar'))['total'] or 0
        
        context['total_harga'] = total_harga
        context['total_transport'] = total_transport
        context['total_pendapatan'] = total_pendapatan
        context['current_period'] = self.request.GET.get('period', 'harian')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        context['record_count'] = qs.count()
        
        # Attach payment method to each item in current page
        current_page_items = context['rekap_list']
        registrasi_ids = [item.id for item in current_page_items]
        if registrasi_ids:
            pemasukan_records = Pemasukan.objects.filter(
                registrasi_id__in=registrasi_ids
            ).select_related('registrasi')
            pemasukan_dict = {p.registrasi_id: p.metode_pembayaran for p in pemasukan_records}
            
            # Add payment method as attribute to each item
            for item in current_page_items:
                item.metode_pembayaran = pemasukan_dict.get(item.id, None)
        
        return context


class NotifikasiListView(LoginRequiredMixin, ListView):
    model = Notifikasi
    template_name = 'core/notifikasi_list.html'
    context_object_name = 'notifikasi_list'
    paginate_by = 25
    
    def get_queryset(self):
        qs = Notifikasi.objects.select_related('pasien', 'registrasi').order_by('-tanggal_notifikasi', '-created_at')
        
        # Filter by read/unread
        filter_type = self.request.GET.get('filter', 'all')
        if filter_type == 'unread':
            qs = qs.filter(sudah_dibaca=False)
        elif filter_type == 'read':
            qs = qs.filter(sudah_dibaca=True)
        
        # Filter by type
        jenis = self.request.GET.get('jenis')
        if jenis:
            qs = qs.filter(jenis_notifikasi=jenis)
        
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Notifikasi.objects.filter(sudah_dibaca=False).count()
        context['current_filter'] = self.request.GET.get('filter', 'all')
        context['current_jenis'] = self.request.GET.get('jenis', '')
        
        # Get available notification types
        jenis_list = Notifikasi.objects.values_list('jenis_notifikasi', flat=True).distinct()
        context['jenis_list'] = [j for j in jenis_list if j]
        
        return context


class MarkNotifikasiReadView(LoginRequiredMixin, View):
    """Mark notification as read via AJAX"""
    def post(self, request, pk):
        try:
            notifikasi = Notifikasi.objects.get(pk=pk)
            notifikasi.sudah_dibaca = True
            notifikasi.save()
            return JsonResponse({'success': True})
        except Notifikasi.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notifikasi tidak ditemukan'}, status=404)


class MarkAllNotifikasiReadView(LoginRequiredMixin, View):
    """Mark all notifications as read"""
    def post(self, request):
        Notifikasi.objects.filter(sudah_dibaca=False).update(sudah_dibaca=True)
        messages.success(request, 'Semua notifikasi telah ditandai sebagai dibaca')
        return redirect('notifikasi_list')


# AJAX Views for Quick Create from Modals
class AjaxCreatePasienView(LoginRequiredMixin, View):
    """Create pasien via AJAX from modal"""
    def post(self, request):
        try:
            # Get form data
            nama_anak = request.POST.get('nama_anak', '').strip()
            tanggal_lahir = request.POST.get('tanggal_lahir', '').strip()
            jenis_kelamin = request.POST.get('jenis_kelamin', '').strip()
            nama_orang_tua = request.POST.get('nama_orang_tua', '').strip()
            alamat = request.POST.get('alamat', '').strip()
            no_wa = request.POST.get('no_wa', '').strip()
            cabang_id = request.POST.get('cabang', '').strip()
            
            # Validate required fields
            if not nama_anak or not tanggal_lahir or not jenis_kelamin:
                return JsonResponse({
                    'success': False, 
                    'error': 'Nama anak, tanggal lahir, dan jenis kelamin harus diisi'
                }, status=400)
            
            # Auto-generate kode_pasien
            from django.db.models import Max
            last_pasien = Pasien.objects.aggregate(Max('id'))['id__max']
            next_id = (last_pasien or 0) + 1
            kode_pasien = f'P{next_id:04d}'
            
            # Create pasien
            pasien = Pasien.objects.create(
                kode_pasien=kode_pasien,
                nama_anak=nama_anak,
                tanggal_lahir=tanggal_lahir,
                jenis_kelamin=jenis_kelamin,
                nama_orang_tua=nama_orang_tua if nama_orang_tua else None,
                alamat=alamat if alamat else None,
                no_wa=no_wa if no_wa else None,
                cabang_id=int(cabang_id) if cabang_id else None
            )
            
            return JsonResponse({
                'success': True,
                'pasien': {
                    'id': pasien.id,
                    'text': f'{pasien.kode_pasien} - {pasien.nama_anak}'
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class AjaxCreateTerapisView(LoginRequiredMixin, View):
    """Create terapis via AJAX from modal"""
    def post(self, request):
        try:
            # Get form data
            nama_terapis = request.POST.get('nama_terapis', '').strip()
            no_hp = request.POST.get('no_hp', '').strip()
            alamat = request.POST.get('alamat', '').strip()
            cabang_id = request.POST.get('cabang', '').strip()
            biaya_transport_default = request.POST.get('biaya_transport_default', '0').strip()
            is_active = request.POST.get('is_active') == 'on'
            
            # Validate required fields
            if not nama_terapis:
                return JsonResponse({
                    'success': False,
                    'error': 'Nama terapis harus diisi'
                }, status=400)
            
            # Create terapis
            terapis = Terapis.objects.create(
                nama_terapis=nama_terapis,
                no_hp=no_hp if no_hp else None,
                alamat=alamat if alamat else None,
                cabang_id=int(cabang_id) if cabang_id else None,
                biaya_transport_default=int(biaya_transport_default.replace('.', '')) if biaya_transport_default else 0,
                is_active=is_active
            )
            
            return JsonResponse({
                'success': True,
                'terapis': {
                    'id': terapis.id,
                    'text': terapis.nama_terapis
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class AjaxCreateJenisTerapiView(LoginRequiredMixin, View):
    """Create jenis terapi via AJAX from modal"""
    def post(self, request):
        try:
            # Get form data
            nama_terapi = request.POST.get('nama_terapi', '').strip()
            kategori_usia_min = request.POST.get('kategori_usia_min', '').strip()
            kategori_usia_max = request.POST.get('kategori_usia_max', '').strip()
            harga = request.POST.get('harga', '0').strip()
            
            # Validate required fields
            if not nama_terapi:
                return JsonResponse({
                    'success': False,
                    'error': 'Nama terapi harus diisi'
                }, status=400)
            
            # Create jenis terapi
            jenis_terapi = JenisTerapi.objects.create(
                nama_terapi=nama_terapi,
                kategori_usia_min=int(kategori_usia_min) if kategori_usia_min else None,
                kategori_usia_max=int(kategori_usia_max) if kategori_usia_max else None,
                harga=int(harga.replace('.', '')) if harga else 0
            )
            
            return JsonResponse({
                'success': True,
                'jenis_terapi': {
                    'id': jenis_terapi.id,
                    'text': jenis_terapi.nama_terapi
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class AjaxGetJenisTerapiPriceView(LoginRequiredMixin, View):
    """Get jenis terapi price via AJAX"""
    def get(self, request, jenis_terapi_id):
        try:
            jenis_terapi = JenisTerapi.objects.get(pk=jenis_terapi_id)
            return JsonResponse({
                'success': True,
                'harga': int(jenis_terapi.harga)  # Convert Decimal to int
            })
        except JenisTerapi.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Jenis terapi tidak ditemukan'
            }, status=404)

class AjaxGetTerapisTransportView(LoginRequiredMixin, View):
    """Get terapis default transport cost via AJAX"""
    def get(self, request, terapis_id):
        try:
            terapis = Terapis.objects.get(pk=terapis_id)
            return JsonResponse({
                'success': True,
                'biaya_transport': int(terapis.biaya_transport_default or 0)  # Convert Decimal to int
            })
        except Terapis.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Terapis tidak ditemukan'
            }, status=404)


class AjaxGetRegistrasiDetailView(LoginRequiredMixin, View):
    """Get registrasi detail including payment info via AJAX"""
    def get(self, request, registrasi_id):
        try:
            from django.db.models import Sum
            registrasi = Registrasi.objects.select_related('pasien', 'jenis_terapi', 'terapis', 'cabang').get(pk=registrasi_id)
            
            # Calculate total already paid
            total_paid = Pemasukan.objects.filter(registrasi_id=registrasi_id).aggregate(
                total=Sum('jumlah')
            )['total'] or 0
            
            total_bayar = float(registrasi.total_bayar or 0)
            sisa = total_bayar - float(total_paid)
            
            return JsonResponse({
                'success': True,
                'registrasi': {
                    'id': registrasi.id,
                    'kode': registrasi.kode_registrasi,
                    'pasien': registrasi.pasien.nama_anak,
                    'jenis_terapi': registrasi.jenis_terapi.nama_terapi,
                    'terapis': registrasi.terapis.nama_terapis if registrasi.terapis else '-',
                    'tanggal_kunjungan': registrasi.tanggal_kunjungan.strftime('%d %b %Y'),
                    'cabang_name': registrasi.cabang.nama_cabang,
                    'total_bayar': total_bayar,
                    'total_paid': float(total_paid),
                    'sisa': sisa,
                }
            })
        except Registrasi.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Registrasi tidak ditemukan'
            }, status=404)


# ============================================================================
# PEMBUKUAN (Accounting) Views
# ============================================================================

class TotalPendapatanView(LoginRequiredMixin, TemplateView):
    """Total income report"""
    template_name = 'core/pembukuan/total_pendapatan.html'
    
    def get(self, request, *args, **kwargs):
        """Handle both normal view and Excel export"""
        if request.GET.get('export') == 'excel':
            return self.export_to_excel(request)
        return super().get(request, *args, **kwargs)
    
    def apply_filters(self, queryset, request):
        """Apply filters from GET parameters"""
        from django.db.models import Q
        from datetime import datetime
        
        # Date range filter
        tanggal_dari = request.GET.get('tanggal_dari')
        tanggal_sampai = request.GET.get('tanggal_sampai')
        
        if tanggal_dari:
            try:
                tanggal_dari_date = datetime.strptime(tanggal_dari, '%Y-%m-%d').date()
                queryset = queryset.filter(tanggal__gte=tanggal_dari_date)
            except:
                pass
        
        if tanggal_sampai:
            try:
                tanggal_sampai_date = datetime.strptime(tanggal_sampai, '%Y-%m-%d').date()
                queryset = queryset.filter(tanggal__lte=tanggal_sampai_date)
            except:
                pass
        
        # Cabang filter
        cabang_id = request.GET.get('cabang_id')
        if cabang_id:
            queryset = queryset.filter(cabang_id=cabang_id)
        
        # Metode Pembayaran filter
        metode = request.GET.get('metode_pembayaran')
        if metode:
            queryset = queryset.filter(metode_pembayaran=metode)
        
        return queryset
    
    def export_to_excel(self, request):
        """Export pemasukan data to Excel file"""
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        from datetime import datetime
        
        # Get data with proper joins and apply filters
        pemasukan_list = Pemasukan.objects.select_related(
            'registrasi__pasien',
            'cabang'
        ).all().order_by('-tanggal')
        
        # Apply filters
        pemasukan_list = self.apply_filters(pemasukan_list, request)
        for pemasukan in pemasukan_list:
            if pemasukan.jumlah_bayar and pemasukan.jumlah and pemasukan.jumlah_bayar > pemasukan.jumlah:
                pemasukan.kembalian = pemasukan.jumlah_bayar - pemasukan.jumlah
            else:
                pemasukan.kembalian = None
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Pemasukan"
        
        # Set column widths
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 20
        ws.column_dimensions['E'].width = 20
        ws.column_dimensions['F'].width = 20
        ws.column_dimensions['G'].width = 20
        
        # Style definitions
        header_fill = PatternFill(start_color="667eea", end_color="667eea", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=12)
        title_font = Font(bold=True, size=14, color="2c3e50")
        border = Border(
            left=Side(style='thin', color='e9ecef'),
            right=Side(style='thin', color='e9ecef'),
            top=Side(style='thin', color='e9ecef'),
            bottom=Side(style='thin', color='e9ecef')
        )
        
        # Title
        ws['A1'] = "LAPORAN PENDAPATAN"
        ws['A1'].font = title_font
        ws.merge_cells('A1:G1')
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 25
        
        # Date
        ws['A2'] = f"Periode: {datetime.now().strftime('%d %B %Y')}"
        ws.merge_cells('A2:G2')
        ws['A2'].alignment = Alignment(horizontal='center')
        
        # Headers
        headers = ['Tanggal', 'Pasien', 'Metode', 'Jumlah Tagihan', 'Jumlah Bayar', 'Kembalian', 'Cabang']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=col)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        ws.row_dimensions[4].height = 20
        
        # Data rows
        for row, pemasukan in enumerate(pemasukan_list, start=5):
            # Get pasien name via join
            pasien_name = '-'
            if pemasukan.registrasi and pemasukan.registrasi.pasien:
                pasien_name = pemasukan.registrasi.pasien.nama_anak
            
            ws.cell(row=row, column=1).value = pemasukan.tanggal.strftime('%d/%m/%Y') if pemasukan.tanggal else '-'
            ws.cell(row=row, column=2).value = pasien_name
            ws.cell(row=row, column=3).value = pemasukan.metode_pembayaran or '-'
            ws.cell(row=row, column=4).value = float(pemasukan.jumlah) if pemasukan.jumlah else 0
            ws.cell(row=row, column=5).value = float(pemasukan.jumlah_bayar) if pemasukan.jumlah_bayar else 0
            ws.cell(row=row, column=6).value = float(pemasukan.kembalian) if pemasukan.kembalian else 0
            ws.cell(row=row, column=7).value = pemasukan.cabang.nama_cabang if pemasukan.cabang else '-'
            
            # Format currency columns
            for col in [4, 5, 6]:
                ws.cell(row=row, column=col).number_format = '#,##0'
            
            # Apply border to all cells
            for col in range(1, 8):
                ws.cell(row=row, column=col).border = border
                ws.cell(row=row, column=col).alignment = Alignment(horizontal='left' if col <= 3 else 'right', vertical='center')
        
        # Response
        from django.http import HttpResponse
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Laporan_Pendapatan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        wb.save(response)
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all pemasukan with select_related for optimization
        pemasukan_list = Pemasukan.objects.select_related(
            'registrasi__pasien',
            'cabang'
        ).all().order_by('-tanggal')
        
        # Apply filters from GET parameters
        pemasukan_list = self.apply_filters(pemasukan_list, self.request)
        
        # Add computed kembalian field to each pemasukan
        for pemasukan in pemasukan_list:
            if pemasukan.jumlah_bayar and pemasukan.jumlah and pemasukan.jumlah_bayar > pemasukan.jumlah:
                pemasukan.kembalian = pemasukan.jumlah_bayar - pemasukan.jumlah
                pemasukan.kembalian_formatted = format_rupiah(int(pemasukan.kembalian))
            else:
                pemasukan.kembalian = None
                pemasukan.kembalian_formatted = None
        
        total = pemasukan_list.aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        count = pemasukan_list.count()
        avg = int(total / count) if count > 0 else 0
        
        # Get filter values from request
        tanggal_dari = self.request.GET.get('tanggal_dari', '')
        tanggal_sampai = self.request.GET.get('tanggal_sampai', '')
        cabang_id = self.request.GET.get('cabang_id', '')
        metode_pembayaran = self.request.GET.get('metode_pembayaran', '')
        
        # Get dinamis cabang list
        from core.models import Cabang
        cabang_list = Cabang.objects.all()
        
        # Metode pembayaran choices
        metode_choices = [
            ('TUNAI', 'Tunai'),
            ('TRANSFER', 'Transfer'),
            ('QRIS', 'QRIS'),
            ('DEBIT', 'Debit'),
            ('KREDIT', 'Kredit'),
        ]
        
        context['pemasukan_list'] = pemasukan_list
        context['total_pendapatan'] = total
        context['total_pendapatan_formatted'] = format_rupiah(total)
        context['avg_pendapatan'] = avg
        context['avg_pendapatan_formatted'] = format_rupiah(avg)
        context['cabang_list'] = cabang_list
        context['metode_choices'] = metode_choices
        context['tanggal_dari'] = tanggal_dari
        context['tanggal_sampai'] = tanggal_sampai
        context['cabang_id'] = cabang_id
        context['metode_pembayaran'] = metode_pembayaran
        return context


class TotalPengeluaranView(LoginRequiredMixin, TemplateView):
    """Total expense report"""
    template_name = 'core/pembukuan/total_pengeluaran.html'
    
    def get(self, request, *args, **kwargs):
        """Handle both normal view and Excel export"""
        if request.GET.get('export') == 'excel':
            return self.export_to_excel(request)
        return super().get(request, *args, **kwargs)
    
    def apply_filters(self, queryset, request):
        """Apply filters from GET parameters"""
        from django.db.models import Q
        from datetime import datetime
        
        # Date range filter
        tanggal_dari = request.GET.get('tanggal_dari')
        tanggal_sampai = request.GET.get('tanggal_sampai')
        
        if tanggal_dari:
            try:
                tanggal_dari_date = datetime.strptime(tanggal_dari, '%Y-%m-%d').date()
                queryset = queryset.filter(tanggal__gte=tanggal_dari_date)
            except:
                pass
        
        if tanggal_sampai:
            try:
                tanggal_sampai_date = datetime.strptime(tanggal_sampai, '%Y-%m-%d').date()
                queryset = queryset.filter(tanggal__lte=tanggal_sampai_date)
            except:
                pass
        
        # Cabang filter
        cabang_id = request.GET.get('cabang_id')
        if cabang_id:
            queryset = queryset.filter(cabang_id=cabang_id)
        
        # Kategori filter
        kategori = request.GET.get('kategori')
        if kategori:
            queryset = queryset.filter(kategori=kategori)
        
        return queryset
    
    def export_to_excel(self, request):
        """Export pengeluaran data to Excel file"""
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        from datetime import datetime
        
        # Get data with proper joins and apply filters
        pengeluaran_list = Pengeluaran.objects.select_related('cabang').all().order_by('-tanggal')
        
        # Apply filters
        pengeluaran_list = self.apply_filters(pengeluaran_list, request)
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Pengeluaran"
        
        # Set column widths
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 30
        ws.column_dimensions['D'].width = 20
        ws.column_dimensions['E'].width = 20
        
        # Style definitions
        header_fill = PatternFill(start_color="f5576c", end_color="f5576c", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=12)
        title_font = Font(bold=True, size=14, color="2c3e50")
        border = Border(
            left=Side(style='thin', color='e9ecef'),
            right=Side(style='thin', color='e9ecef'),
            top=Side(style='thin', color='e9ecef'),
            bottom=Side(style='thin', color='e9ecef')
        )
        
        # Title
        ws['A1'] = "LAPORAN PENGELUARAN"
        ws['A1'].font = title_font
        ws.merge_cells('A1:E1')
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 25
        
        # Date
        ws['A2'] = f"Periode: {datetime.now().strftime('%d %B %Y')}"
        ws.merge_cells('A2:E2')
        ws['A2'].alignment = Alignment(horizontal='center')
        
        # Headers
        headers = ['Tanggal', 'Kategori', 'Keterangan', 'Cabang', 'Jumlah']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=col)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        ws.row_dimensions[4].height = 20
        
        # Data rows
        for row, pengeluaran in enumerate(pengeluaran_list, start=5):
            ws.cell(row=row, column=1).value = pengeluaran.tanggal.strftime('%d/%m/%Y') if pengeluaran.tanggal else '-'
            ws.cell(row=row, column=2).value = pengeluaran.kategori or '-'
            ws.cell(row=row, column=3).value = pengeluaran.keterangan or ''
            ws.cell(row=row, column=4).value = pengeluaran.cabang.nama_cabang if pengeluaran.cabang else '-'
            ws.cell(row=row, column=5).value = float(pengeluaran.jumlah) if pengeluaran.jumlah else 0
            
            # Format currency column
            ws.cell(row=row, column=5).number_format = '#,##0'
            
            # Apply border to all cells
            for col in range(1, 6):
                ws.cell(row=row, column=col).border = border
                ws.cell(row=row, column=col).alignment = Alignment(horizontal='left' if col <= 4 else 'right', vertical='center')
        
        # Response
        from django.http import HttpResponse
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Laporan_Pengeluaran_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        wb.save(response)
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all pengeluaran with select_related for optimization
        pengeluaran_list = Pengeluaran.objects.select_related('cabang').all().order_by('-tanggal')
        
        # Apply filters from GET parameters
        pengeluaran_list = self.apply_filters(pengeluaran_list, self.request)
        
        total = pengeluaran_list.aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        count = pengeluaran_list.count()
        avg = int(total / count) if count > 0 else 0
        
        # Get filter values from request
        tanggal_dari = self.request.GET.get('tanggal_dari', '')
        tanggal_sampai = self.request.GET.get('tanggal_sampai', '')
        cabang_id = self.request.GET.get('cabang_id', '')
        kategori_filter = self.request.GET.get('kategori', '')
        
        # Get dinamis cabang list
        from core.models import Cabang
        cabang_list = Cabang.objects.all()
        
        # Get unique kategori from pengeluaran
        kategori_choices = Pengeluaran.objects.filter(kategori__isnull=False).values_list('kategori', flat=True).distinct().order_by('kategori')
        
        context['pengeluaran_list'] = pengeluaran_list
        context['total_pengeluaran'] = total
        context['total_pengeluaran_formatted'] = format_rupiah(total)
        context['avg_pengeluaran'] = avg
        context['avg_pengeluaran_formatted'] = format_rupiah(avg)
        context['cabang_list'] = cabang_list
        context['kategori_choices'] = kategori_choices
        context['tanggal_dari'] = tanggal_dari
        context['tanggal_sampai'] = tanggal_sampai
        context['cabang_id'] = cabang_id
        context['kategori'] = kategori_filter
        return context


class RekapPasienTerapisView(LoginRequiredMixin, TemplateView):
    """Summary of number of patients per therapist"""
    template_name = 'core/pembukuan/rekap_pasien_terapis.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get summary: count registrasi per terapis
        from django.db.models import Count
        terapis_list = Terapis.objects.annotate(
            jumlah_pasien=Count('registrasi')
        ).order_by('-jumlah_pasien')
        
        total_registrasi = Registrasi.objects.count()
        
        context['terapis_list'] = terapis_list
        context['total_terapis'] = terapis_list.count()
        context['total_registrasi'] = total_registrasi
        return context


class RekapTransportTerapisView(LoginRequiredMixin, TemplateView):
    """Summary of transport money per therapist"""
    template_name = 'core/pembukuan/rekap_transport_terapis.html'
    
    def get_context_data(self, **kwargs):
        import json
        context = super().get_context_data(**kwargs)
        
        # Get summary: total biaya_transport per terapis
        terapis_transport = []
        for terapis in Terapis.objects.all():
            registrasi = Registrasi.objects.filter(terapis=terapis)
            total_transport = registrasi.aggregate(Sum('biaya_transport'))['biaya_transport__sum'] or 0
            terapis_transport.append({
                'terapis': terapis,
                'total_transport': total_transport,
                'total_transport_formatted': format_rupiah(total_transport),
                'jumlah_registrasi': registrasi.count()
            })
        
        # Sort by total_transport descending
        terapis_transport.sort(key=lambda x: x['total_transport'], reverse=True)
        grand_total = sum(item['total_transport'] for item in terapis_transport)
        
        # Prepare chart data for distribution
        terapis_names = [item['terapis'].nama_terapis for item in terapis_transport]
        transport_amounts = [float(item['total_transport']) for item in terapis_transport]
        
        # Color palette for chart
        colors = [
            '#0d6efd', '#6c757d', '#198754', '#dc3545', '#ffc107',
            '#0dcaf0', '#6f42c1', '#d63384', '#fd7e14', '#20c997',
            '#e83e8c', '#17a2b8', '#007bff', '#28a745', '#dc3545',
        ]
        # Cycle colors if more terapis than colors
        chart_colors = [colors[i % len(colors)] for i in range(len(terapis_names))]
        
        context['terapis_transport'] = terapis_transport
        context['grand_total'] = grand_total
        context['grand_total_formatted'] = format_rupiah(grand_total)
        context['terapis_names_json'] = json.dumps(terapis_names)
        context['transport_amounts_json'] = json.dumps(transport_amounts)
        context['chart_colors_json'] = json.dumps(chart_colors)
        return context


class SaldoAkhirView(LoginRequiredMixin, TemplateView):
    """Final balance report (Total Income - Total Expenses)"""
    template_name = 'core/pembukuan/saldo_akhir.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate totals
        total_pendapatan = Pemasukan.objects.aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        total_pengeluaran = Pengeluaran.objects.aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        saldo_akhir = total_pendapatan - total_pengeluaran
        
        context['total_pendapatan'] = total_pendapatan
        context['total_pendapatan_formatted'] = format_rupiah(total_pendapatan)
        context['total_pengeluaran'] = total_pengeluaran
        context['total_pengeluaran_formatted'] = format_rupiah(total_pengeluaran)
        context['saldo_akhir'] = saldo_akhir
        context['saldo_akhir_formatted'] = format_rupiah(saldo_akhir)
        context['status'] = 'surplus' if saldo_akhir > 0 else 'defisit' if saldo_akhir < 0 else 'seimbang'
        
        return context


# ============================================
# PENGATURAN (SETTINGS)
# ============================================

class AppSettingsView(LoginRequiredMixin, View):
    """View for managing app settings (font size and logo)."""
    login_url = '/login/'
    template_name = 'core/pengaturan.html'

    def get(self, request):
        from .models import AppSettings
        from .forms import AppSettingsForm
        
        settings = AppSettings.get_settings()
        form = AppSettingsForm(instance=settings)
        
        context = {
            'form': form,
            'settings': settings,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        from .models import AppSettings
        from .forms import AppSettingsForm
        
        settings = AppSettings.get_settings()
        form = AppSettingsForm(request.POST, request.FILES, instance=settings)
        
        if form.is_valid():
            settings = form.save(commit=False)
            settings.updated_by = request.user
            settings.save()
            messages.success(request, 'Pengaturan berhasil disimpan!')
            return redirect('app_settings')
        
        context = {
            'form': form,
            'settings': settings,
        }
        return render(request, self.template_name, context)


# ============================================
# USER MANAGEMENT
# ============================================

class UserListView(LoginRequiredMixin, ListView):
    """List all users."""
    model = User
    template_name = 'core/user_list.html'
    context_object_name = 'users'
    paginate_by = 25

    def get_queryset(self):
        return User.objects.all().order_by('-created_at')


class UserCreateView(LoginRequiredMixin, View):
    """Create new user."""
    login_url = '/login/'
    template_name = 'core/user_form.html'

    def get(self, request):
        from .forms import UserCreateForm
        form = UserCreateForm()
        context = {
            'form': form,
            'is_create': True,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        from .forms import UserCreateForm
        form = UserCreateForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} berhasil dibuat!')
            return redirect('user_list')
        
        context = {
            'form': form,
            'is_create': True,
        }
        return render(request, self.template_name, context)


class UserEditView(LoginRequiredMixin, View):
    """Edit existing user."""
    login_url = '/login/'
    template_name = 'core/user_form.html'

    def get(self, request, pk):
        from .forms import UserForm
        user = User.objects.get(pk=pk)
        form = UserForm(instance=user)
        context = {
            'form': form,
            'is_create': False,
            'user_obj': user,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        from .forms import UserForm
        user = User.objects.get(pk=pk)
        form = UserForm(request.POST, instance=user)
        
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} berhasil diupdate!')
            return redirect('user_list')
        
        context = {
            'form': form,
            'is_create': False,
            'user_obj': user,
        }
        return render(request, self.template_name, context)


class UserToggleActiveView(LoginRequiredMixin, View):
    """Toggle user active status (activate/deactivate)."""
    login_url = '/login/'

    def post(self, request, pk):
        user = User.objects.get(pk=pk)
        user.is_active = not user.is_active
        user.save()
        
        status = 'diaktifkan' if user.is_active else 'dinonaktifkan'
        messages.success(request, f'User {user.username} berhasil {status}!')
        return redirect('user_list')

# ============================================
# NOTIFICATION GENERATION
# ============================================

class GenerateNotificationsView(LoginRequiredMixin, View):
    """Generate notifications on-demand."""
    login_url = '/login/'

    def post(self, request):
        from core.services.notification_service import generate_all_notifications
        from django.http import JsonResponse
        
        try:
            result = generate_all_notifications()
            messages.success(
                request,
                f"✓ Notifikasi berhasil dibuat! Total: {result['total_created']} notifikasi baru"
            )
            return JsonResponse({
                'success': True,
                'total_created': result['total_created'],
                'details': {k: v['message'] for k, v in result['details'].items()}
            })
        except Exception as e:
            messages.error(request, f'Error generating notifications: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)