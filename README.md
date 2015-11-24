### Dependencies
- Python-2.7
- NumPy-1.10 `pip install numpy`
- BitVector-3.3.2 (Optional) `pip install BitVector`

### Module Descriptions
- `bv_gf.py`      -- an unoptimized general implementation using BitVector module
- `config.py`     -- simple configurations
- `driver.py`     -- main entry; used to setup RAID system and do experiments
- `gf.py`         -- a tuned implementation
- `log_helper.py` -- logging utilities (with log.yaml)
- `raid.py`       -- abstract RAID class containing several common APIs
- `raid4.py`      -- RAID4 implementation
- `raid5.py`      -- RAID5 implementation
- `raid6.py`      -- RAID6 implementation
- `utils.py`      -- common utilities

### Features:
- basic operations:
  - read --> check
  - write
  - recover <=2 disks
  - detect 1 corrupted disk
- find which disk is corrupted
- recover 2-disk case
- mutable files
- RAID4 and RAID5
- concurrent actual read/write
- optimized and raw gf8 multiplication
- data types can be:
  - text-only
  - arbitrary bytes

### TODO:
- unittest
- deal with socket
