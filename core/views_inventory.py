"""
Inventory Management Views
"""
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from django.contrib import messages
from decimal import Decimal

from .models import (
    KategoriBarang, BarangInventory, StokMasuk, PemakaianBarang,
    Cabang, Registrasi
)
from .forms import (
    KategoriBarangForm, BarangInventoryForm, StokMasukForm, PemakaianBarangForm
)


class KategoriBarangListView(LoginRequiredMixin, ListView):
    """List kategori barang"""
    model = KategoriBarang
    template_name = 'core/kategori_barang_list.html'
    context_object_name = 'kategori_list'
    paginate_by = 20
    login_url = '/login/'

    def get_queryset(self):
        qs = KategoriBarang.objects.all().order_by('nama_kategori')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(nama_kategori__icontains=q)
        return qs


class KategoriBarangCreateView(LoginRequiredMixin, CreateView):
    """Tambah kategori barang"""
    model = KategoriBarang
    form_class = KategoriBarangForm
    template_name = 'core/kategori_barang_form.html'
    success_url = reverse_lazy('kategori_barang_list')
    login_url = '/login/'

    def form_valid(self, form):
        messages.success(self.request, 'Kategori barang berhasil ditambahkan!')
        return super().form_valid(form)


class KategoriBarangUpdateView(LoginRequiredMixin, UpdateView):
    """Edit kategori barang"""
    model = KategoriBarang
    form_class = KategoriBarangForm
    template_name = 'core/kategori_barang_form.html'
    success_url = reverse_lazy('kategori_barang_list')
    login_url = '/login/'

    def form_valid(self, form):
        messages.success(self.request, 'Kategori barang berhasil diupdate!')
        return super().form_valid(form)


class BarangInventoryListView(LoginRequiredMixin, ListView):
    """List barang inventory dengan alert stok"""
    model = BarangInventory
    template_name = 'core/barang_inventory_list.html'
    context_object_name = 'barang_list'
    paginate_by = 20
    login_url = '/login/'

    def get_queryset(self):
        qs = BarangInventory.objects.select_related('kategori', 'cabang').filter(is_active=True).order_by('nama_barang')
        
        # Filter
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(nama_barang__icontains=q) | Q(kode_barang__icontains=q))
        
        kategori_id = self.request.GET.get('kategori')
        if kategori_id:
            qs = qs.filter(kategori_id=kategori_id)
        
        cabang_id = self.request.GET.get('cabang')
        if cabang_id:
            qs = qs.filter(cabang_id=cabang_id)
        
        status = self.request.GET.get('status')
        if status == 'rendah':
            # Can't filter by property in QuerySet, will handle in template
            pass
        elif status == 'habis':
            qs = qs.filter(stok_tersedia=0)
        
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kategori_list'] = KategoriBarang.objects.all()
        context['cabang_list'] = Cabang.objects.all()
        
        # Stats
        all_barang = BarangInventory.objects.filter(is_active=True)
        context['total_barang'] = all_barang.count()
        context['stok_rendah_count'] = len([b for b in all_barang if b.is_stok_rendah])
        context['stok_habis_count'] = all_barang.filter(stok_tersedia=0).count()
        
        return context


class BarangInventoryCreateView(LoginRequiredMixin, CreateView):
    """Tambah barang inventory"""
    model = BarangInventory
    form_class = BarangInventoryForm
    template_name = 'core/barang_inventory_form.html'
    success_url = reverse_lazy('barang_inventory_list')
    login_url = '/login/'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Barang inventory berhasil ditambahkan!')
        return super().form_valid(form)


class BarangInventoryUpdateView(LoginRequiredMixin, UpdateView):
    """Edit barang inventory"""
    model = BarangInventory
    form_class = BarangInventoryForm
    template_name = 'core/barang_inventory_form.html'
    success_url = reverse_lazy('barang_inventory_list')
    login_url = '/login/'

    def form_valid(self, form):
        messages.success(self.request, 'Barang inventory berhasil diupdate!')
        return super().form_valid(form)


class StokMasukListView(LoginRequiredMixin, ListView):
    """List history stok masuk"""
    model = StokMasuk
    template_name = 'core/stok_masuk_list.html'
    context_object_name = 'stok_masuk_list'
    paginate_by = 20
    login_url = '/login/'

    def get_queryset(self):
        qs = StokMasuk.objects.select_related('barang', 'cabang', 'created_by').order_by('-tanggal_masuk', '-created_at')
        
        # Filter
        barang_id = self.request.GET.get('barang')
        if barang_id:
            qs = qs.filter(barang_id=barang_id)
        
        cabang_id = self.request.GET.get('cabang')
        if cabang_id:
            qs = qs.filter(cabang_id=cabang_id)
        
        tanggal_dari = self.request.GET.get('tanggal_dari')
        tanggal_sampai = self.request.GET.get('tanggal_sampai')
        if tanggal_dari:
            qs = qs.filter(tanggal_masuk__gte=tanggal_dari)
        if tanggal_sampai:
            qs = qs.filter(tanggal_masuk__lte=tanggal_sampai)
        
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barang_list'] = BarangInventory.objects.filter(is_active=True).order_by('nama_barang')
        context['cabang_list'] = Cabang.objects.all()
        return context


class StokMasukCreateView(LoginRequiredMixin, CreateView):
    """Tambah stok masuk (restock)"""
    model = StokMasuk
    form_class = StokMasukForm
    template_name = 'core/stok_masuk_form.html'
    success_url = reverse_lazy('stok_masuk_list')
    login_url = '/login/'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        barang = form.instance.barang
        messages.success(
            self.request, 
            f'Stok masuk berhasil dicatat! Stok {barang.nama_barang} sekarang: {barang.stok_tersedia} {barang.satuan}'
        )
        return response


class PemakaianBarangListView(LoginRequiredMixin, ListView):
    """List history pemakaian barang"""
    model = PemakaianBarang
    template_name = 'core/pemakaian_barang_list.html'
    context_object_name = 'pemakaian_list'
    paginate_by = 20
    login_url = '/login/'

    def get_queryset(self):
        qs = PemakaianBarang.objects.select_related(
            'barang', 'registrasi', 'cabang', 'created_by'
        ).order_by('-tanggal_pakai', '-created_at')
        
        # Filter
        barang_id = self.request.GET.get('barang')
        if barang_id:
            qs = qs.filter(barang_id=barang_id)
        
        cabang_id = self.request.GET.get('cabang')
        if cabang_id:
            qs = qs.filter(cabang_id=cabang_id)
        
        tanggal_dari = self.request.GET.get('tanggal_dari')
        tanggal_sampai = self.request.GET.get('tanggal_sampai')
        if tanggal_dari:
            qs = qs.filter(tanggal_pakai__gte=tanggal_dari)
        if tanggal_sampai:
            qs = qs.filter(tanggal_pakai__lte=tanggal_sampai)
        
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barang_list'] = BarangInventory.objects.filter(is_active=True).order_by('nama_barang')
        context['cabang_list'] = Cabang.objects.all()
        
        # Total nilai pemakaian
        qs = self.get_queryset()
        total_nilai = sum([p.nilai_pemakaian for p in qs])
        context['total_nilai_pemakaian'] = total_nilai
        
        return context


class PemakaianBarangCreateView(LoginRequiredMixin, CreateView):
    """Catat pemakaian barang"""
    model = PemakaianBarang
    form_class = PemakaianBarangForm
    template_name = 'core/pemakaian_barang_form.html'
    success_url = reverse_lazy('pemakaian_barang_list')
    login_url = '/login/'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter only active barang
        form.fields['barang'].queryset = BarangInventory.objects.filter(is_active=True).order_by('nama_barang')
        # Show recent registrations
        form.fields['registrasi'].queryset = Registrasi.objects.filter(
            is_deleted=False
        ).select_related('pasien').order_by('-tanggal_kunjungan')[:100]
        return form

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        try:
            response = super().form_valid(form)
            barang = form.instance.barang
            messages.success(
                self.request, 
                f'Pemakaian barang berhasil dicatat! Sisa stok {barang.nama_barang}: {barang.stok_tersedia} {barang.satuan}'
            )
            # Alert jika stok rendah
            if barang.is_stok_rendah:
                messages.warning(
                    self.request,
                    f'⚠️ Stok {barang.nama_barang} sudah rendah! Segera lakukan restock.'
                )
            return response
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)


class LaporanInventoryView(LoginRequiredMixin, TemplateView):
    """Dashboard laporan inventory"""
    template_name = 'core/laporan_inventory.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filter parameters
        cabang_id = self.request.GET.get('cabang')
        kategori_id = self.request.GET.get('kategori')
        
        # Base queryset
        barang_qs = BarangInventory.objects.filter(is_active=True)
        if cabang_id:
            barang_qs = barang_qs.filter(cabang_id=cabang_id)
        if kategori_id:
            barang_qs = barang_qs.filter(kategori_id=kategori_id)
        
        # Stats
        context['total_barang'] = barang_qs.count()
        context['total_nilai_stok'] = sum([b.stok_tersedia * b.harga_satuan for b in barang_qs])
        context['stok_rendah_list'] = [b for b in barang_qs if b.is_stok_rendah]
        context['stok_habis_list'] = barang_qs.filter(stok_tersedia=0)
        
        # Kategori breakdown
        kategori_stats = []
        for kategori in KategoriBarang.objects.all():
            barang_kategori = barang_qs.filter(kategori=kategori)
            if barang_kategori.exists():
                kategori_stats.append({
                    'kategori': kategori,
                    'jumlah_barang': barang_kategori.count(),
                    'total_nilai': sum([b.stok_tersedia * b.harga_satuan for b in barang_kategori]),
                })
        context['kategori_stats'] = kategori_stats
        
        # Recent activity
        context['recent_stok_masuk'] = StokMasuk.objects.select_related('barang').order_by('-created_at')[:10]
        context['recent_pemakaian'] = PemakaianBarang.objects.select_related('barang').order_by('-created_at')[:10]
        
        # Filters
        context['cabang_list'] = Cabang.objects.all()
        context['kategori_list'] = KategoriBarang.objects.all()
        
        return context
