# -*- coding: utf-8 -*-
"""
Script ini merupakan versi aman dari Untitled0.ipynb
Dapat dijalankan di:
✅ Google Colab
✅ GitHub Codespaces
✅ Streamlit Cloud
✅ Lokal (Python murni)
Tanpa error karena tanda '!' atau subprocess.
"""

# =====================================================
# === 1. Install / Import Library ===
# =====================================================
import importlib
import sys
import subprocess

# Daftar package yang dibutuhkan
packages = ["xarray", "netCDF4", "numpy", "matplotlib", "cartopy"]

# Coba impor setiap package, install jika belum ada
for pkg in packages:
    try:
        importlib.import_module(pkg)
    except ImportError:
        print(f"📦 Menginstal {pkg} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# Setelah semua terpasang, baru import
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os

# =====================================================
# === 2. Buka file wrfout ===
# =====================================================
# Pastikan file ada di direktori kerja
ncfile = '/content/wrfout_d03_2024-03-12_00:00:00'

if not os.path.exists(ncfile):
    print(f"⚠️ File {ncfile} tidak ditemukan.")
    print("Silakan ubah variabel `ncfile` ke lokasi file NetCDF yang sesuai.")
    sys.exit(1)

# Buka file dengan xarray
ds = xr.open_dataset(ncfile)

# =====================================================
# === 3. Ambil variabel curah hujan ===
# =====================================================
rainc = ds['RAINC']    # Convective rain (mm)
rainnc = ds['RAINNC']  # Non-convective rain (mm)
rain_total = rainc + rainnc

# =====================================================
# === 4. Hitung rain rate (mm/jam) ===
# =====================================================
rain_diff = rain_total.diff(dim='Time')
time_diff = (rain_total['Time'].diff(dim='Time') / np.timedelta64(1, 'h')).astype(float)
time_diff_3d = time_diff[:, None, None]
rain_rate = rain_diff / time_diff_3d
rain_rate.name = 'rain_rate'
rain_rate.attrs['units'] = 'mm/h'

# =====================================================
# === 5. Plot peta rain rate ===
# =====================================================
lat = ds['XLAT'].isel(Time=0)
lon = ds['XLONG'].isel(Time=0)
rain_plot = rain_rate.isel(Time=-1)

plt.figure(figsize=(8, 6))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
plt.title("Rain Rate (mm/jam)")
p = plt.pcolormesh(lon, lat, rain_plot, cmap='Blues', transform=ccrs.PlateCarree())
plt.colorbar(p, ax=ax, label='mm/jam')
plt.tight_layout()

# Simpan grafik sebagai file (agar bisa dilihat di GitHub Action / Streamlit)
output_png = "rain_rate_map.png"
plt.savefig(output_png, dpi=150)
print(f"🖼️ Peta curah hujan disimpan ke: {output_png}")

# =====================================================
# === 6. Simpan hasil rain rate ke NetCDF baru ===
# =====================================================
output_nc = '/content/rain_rate_wrf.nc'
rain_rate.to_netcdf(output_nc)
print(f"✅ Rain rate disimpan sebagai {output_nc}")
