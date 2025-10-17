# -*- coding: utf-8 -*-
"""
Script Aman Visualisasi Rain Rate dari WRF Output
==================================================
Dapat dijalankan di:
✅ GitHub Codespaces / Actions
✅ Streamlit Cloud
✅ Google Colab
✅ Lokal (Python murni)

Fungsi:
- Membaca file WRF (NetCDF)
- Menghitung Rain Rate (mm/jam)
- Membuat peta curah hujan (rain rate)
- Menyimpan hasil ke NetCDF dan PNG

Tidak menggunakan tanda '!' (Colab magic) dan tidak error pada subprocess.
"""

# =====================================================
# === 1. Import dan pastikan library terpasang ===
# =====================================================
import importlib
import sys
import subprocess
import os

# Daftar package yang diperlukan
REQUIRED_PACKAGES = ["xarray", "netCDF4", "numpy", "matplotlib", "cartopy"]

def ensure_packages_installed(packages):
    """Pastikan semua package sudah terinstal."""
    for pkg in packages:
        try:
            importlib.import_module(pkg)
        except ImportError:
            print(f"📦 Menginstal {pkg} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

ensure_packages_installed(REQUIRED_PACKAGES)

# Setelah semua terinstal, baru import modulnya
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# =====================================================
# === 2. Lokasi file input/output ===
# =====================================================
# Sesuaikan path dengan lokasi file di repo GitHub kamu
# Misal: file wrfout disimpan di folder "data/"
DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Ubah sesuai nama file NetCDF kamu
ncfile = os.path.join(DATA_DIR, "wrfout_d03_2024-03-12_00:00:00")

if not os.path.exists(ncfile):
    print(f"⚠️ File {ncfile} tidak ditemukan.")
    print("Silakan upload file WRF NetCDF ke folder 'data/'.")
    sys.exit(0)

# =====================================================
# === 3. Buka dataset WRF ===
# =====================================================
print(f"📂 Membuka file: {ncfile}")
ds = xr.open_dataset(ncfile)

# =====================================================
# === 4. Hitung total curah hujan dan rain rate ===
# =====================================================
rainc = ds["RAINC"]    # Convective rain (mm)
rainnc = ds["RAINNC"]  # Non-convective rain (mm)
rain_total = rainc + rainnc

# Hitung perbedaan antar waktu
rain_diff = rain_total.diff(dim="Time")

# Hitung selisih waktu dalam jam
time_diff = (rain_total["Time"].diff(dim="Time") / np.timedelta64(1, "h")).astype(float)
time_diff_3d = time_diff[:, None, None]

# Rain rate = Δrain / Δt
rain_rate = rain_diff / time_diff_3d
rain_rate.name = "rain_rate"
rain_rate.attrs["units"] = "mm/h"

print("✅ Perhitungan rain rate selesai.")

# =====================================================
# === 5. Plot peta rain rate terakhir ===
# =====================================================
lat = ds["XLAT"].isel(Time=0)
lon = ds["XLONG"].isel(Time=0)
rain_plot = rain_rate.isel(Time=-1)

plt.figure(figsize=(9, 7))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
plt.title("Rain Rate (mm/jam) — Waktu Terakhir", fontsize=12)
p = plt.pcolormesh(lon, lat, rain_plot, cmap="Blues", transform=ccrs.PlateCarree())
plt.colorbar(p, ax=ax, label="mm/jam")
plt.tight_layout()

# Simpan hasil plot ke file
output_png = os.path.join(os.getcwd(), "rain_rate_map.png")
plt.savefig(output_png, dpi=150)
plt.close()
print(f"🖼️ Peta curah hujan disimpan ke: {output_png}")

# =====================================================
# === 6. Simpan hasil rain rate ke NetCDF ===
# =====================================================
output_nc = os.path.join(os.getcwd(), "rain_rate_wrf.nc")
rain_rate.to_netcdf(output_nc)
print(f"✅ Rain rate disimpan sebagai: {output_nc}")

print("\n🎉 Proses selesai tanpa error.")
