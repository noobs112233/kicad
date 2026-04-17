# Arduino Mega 2560 — KiCad 原理圖繪製練習

對照 `MEGA2560_Rev3e_sch.pdf` 與完整 KiCad 參考專案，使用 **KiCad 9.0** 分工繪製 Arduino Mega 2560 Rev3 原理圖。

---

## Repo 結構

```
kicad/
├── Arduino_Mega2560_Practice/      ← 學生繪製的空白專案（每人畫一個 Section）
│   ├── Arduino_Mega2560_Practice.kicad_pro
│   ├── Arduino_Mega2560_Practice.kicad_sch     (root，4 個子頁框)
│   ├── Section_01_USB_ATmega16U2.kicad_sch     ← 空白
│   ├── Section_02_ATmega2560_MCU.kicad_sch     ← 空白
│   ├── Section_03_Power_Supply.kicad_sch       ← 空白
│   ├── Section_04_Arduino_Headers.kicad_sch    ← 空白
│   ├── Arduino_Mega2560_Lib.kicad_sym          ← 專案符號庫（已預掛 footprint）
│   ├── Arduino_Mega2560_FP.pretty/             ← 自訂 footprint 庫
│   ├── sym-lib-table                           ← 符號庫掛載設定
│   └── fp-lib-table                            ← Footprint 庫掛載設定
│
├── Arduino_Mega2560_Rev3/          ← 完整參考專案（schematic only，無 PCB layout）
│   ├── Arduino Mega 2560.kicad_pro
│   ├── Arduino Mega 2560.kicad_sch             (root)
│   ├── ATMEGA2560-16AU.kicad_sch
│   ├── Power.kicad_sch
│   ├── Headers.kicad_sch
│   ├── Arduino Mega 2560.kicad_sym
│   ├── Arduino Mega 2560.pretty/
│   └── Arduino_Mega2560_Rev3_Schematic.pdf
│
├── PPT/                            ← 課程投影片
├── MEGA2560_Rev3e_sch.pdf          ← 官方參考原理圖
├── arduino_mega2560_BOM.csv        ← 完整 BOM (62 個位號)
└── README.md
```

---

## 分工架構

原理圖分為 **4 個子頁面**，每人負責一個區塊：

| 頁面 | 檔案 | 負責內容 |
|------|------|---------|
| Page 2 | `Section_01_USB_ATmega16U2.kicad_sch` | USB-C 接頭、ESD 保護、ATmega16U2 USB Bridge、晶振 Y2 |
| Page 3 | `Section_02_ATmega2560_MCU.kicad_sch` | ATmega2560 主控 MCU、去耦電容、Reset 電路、晶振 Y1 |
| Page 4 | `Section_03_Power_Supply.kicad_sch` | DC 電源座、NCP1117 5V、LP2985 3.3V、PMOS、LMV358 |
| Page 5 | `Section_04_Arduino_Headers.kicad_sch` | 所有 Arduino 腳位排針（數位/類比/電源） |

---

## 開啟專案

1. 啟動 **KiCad 9.0**
2. `File > Open Project`
3. 選 `Arduino_Mega2560_Practice/Arduino_Mega2560_Practice.kicad_pro`
4. 從 Project Manager 雙擊原理圖開啟 Eeschema
5. 在頁面選擇器切到你負責的 Section 開始繪製

---

## 符號庫 / Footprint 庫使用

### 自動掛載（已設定好，**不需要手動加**）

專案內附的 `sym-lib-table` 與 `fp-lib-table` 已經用 `${KIPRJMOD}` 路徑指向專案資料夾，**只要從 `.kicad_pro` 開啟專案就會自動載入**：

| Library 類型 | 名稱 | 路徑 | 內容 |
|------|------|------|------|
| 符號庫 (Symbol) | `Arduino_Mega2560_Lib` | `Arduino_Mega2560_Lib.kicad_sym` | 92 個符號（ATmega2560、ATmega16U2、被動元件、連接器…） |
| Footprint 庫 | `Arduino_Mega2560_FP` | `Arduino_Mega2560_FP.pretty/` | 4 個自訂 footprint（電源座、針腳、按鍵、Polyfuse） |

> 每個符號已預先連結對應 footprint，**畫原理圖時不需要再指定 footprint**。

### 放置元件

- **Eeschema (原理圖)**: `Place > Add Symbol` (快捷鍵 `A`) → 在 Filter 輸入 `Arduino_Mega2560_Lib:` → 選元件
- **Pcbnew (Footprint)**: `Place > Add Footprint` (快捷鍵 `A`) → Filter 輸入 `Arduino_Mega2560_FP:`

### 看不到符號庫怎麼辦？

如果 Eeschema 找不到 `Arduino_Mega2560_Lib`：

1. `Preferences > Manage Symbol Libraries`
2. 切到 **Project Specific Libraries** 頁籤
3. 確認有一筆 `Arduino_Mega2560_Lib` 指向 `${KIPRJMOD}/Arduino_Mega2560_Lib.kicad_sym`
4. 若無，按 `+` 新增；如果路徑紅字，KiCad 沒讀到專案 → 確認你是用 `.kicad_pro` 開啟，不要直接開 `.kicad_sch`

Footprint 庫同理：`Preferences > Manage Footprint Libraries > Project Specific Libraries`。

---

## 完整參考原理圖

需要對照已完成的版本時，開 `Arduino_Mega2560_Rev3/Arduino Mega 2560.kicad_pro`，含完整 4 頁 schematic。
**此參考專案不附 PCB layout** — layout 要自己畫。

或直接看 PDF：`Arduino_Mega2560_Rev3/Arduino_Mega2560_Rev3_Schematic.pdf`、`MEGA2560_Rev3e_sch.pdf`。

---

## BOM

`arduino_mega2560_BOM.csv` 列出 62 個位號（Reference / Value / Description / Footprint），可以對照確認元件數量與規格。

---

## BOM ↔ 符號庫 對照表

> ⚠️ 符號庫的命名不統一 — 有些用「料號」(`ATmega2560_16AU`)、有些用「通用封裝名」(`Fuse_1812`、`C_SMD_0603`)。直接搜料號常常找不到，請對照下表搜尋：

### 被動元件
| BOM Ref | 元件 | **在符號庫搜這個名字** |
|---|---|---|
| C1–C16 | 0603 SMD 電容 | `C_SMD_0603` |
| PC1, PC2 | 47µF 鋁電解 (THT) | `C_Pol` |
| R1, R2 | 0603 SMD 電阻 | `R_SMD_0603` |
| RN1–RN5 | SIP8 排阻 | `RArray_4x0612` |
| L1 | Ferrite bead 0805 | `FerriteBead_0805` |
| **F1** | **PPTC182LFBN-RC Polyfuse 1812** | **`Fuse_1812`** ← 不是料號！ |

### 主動元件
| BOM Ref | 元件 | **搜這個名字** |
|---|---|---|
| IC1 | LD1117 5V LDO (SOT-223) | `NCP1117_5_0_SOT223` ⚠️ 符號名是 NCP1117，pin out 相容 |
| IC3 | ATmega2560 | `ATmega2560_16AU` |
| IC4 | ATmega16U2 | `ATmega16U2_MU` |
| IC6 | LP2985 3.3V LDO | `LP2985_3_3` |
| IC7 | LMV358 op-amp | `LMV358` |
| T1 | PMV48XP P-MOSFET | `Q_PMOS_GSD` |
| D1 | M7 整流二極體 (SMB) | `D_SMB` |
| D2, D3 | CD1206 高速二極體 | `D_1206` |
| Z1, Z2 | 0603 ESD Varistor | `Varistor_0603` |

### 振盪器 / 開關 / LED
| BOM Ref | 元件 | **搜這個名字** |
|---|---|---|
| Y1 | CSTCE16M0V53-R0 三腳陶瓷諧振器 | `Resonator_3Pin` |
| Y2 | 16MHz HC-49/S 晶振 | `Crystal_HC49` |
| RESET | TS42 Tactile 按鍵 | `SW_Reset` |
| ON / L / RX / TX | 0805 LED | `LED_0805` |

### 連接器
| BOM Ref | 元件 | **搜這個名字** |
|---|---|---|
| X1 | DC 電源座 2.1mm | `Barrel_Jack_Switch` |
| X2 | USB Type-B (BOM) ※ 符號庫實作為 USB-C | `USB_C_16P` ⚠️ 與 BOM 不一致，依 Rev3e 改為 USB-C |
| ICSP, ICSP1 | 2x3 排針 | `Header_2x03` |
| JP5 | 2x2 排針 | `Header_2x02` |
| JP6 | 1x10 排母 | `Conn_01x10` |
| POWER, ADCH, ADCL, COMMUNICATION, PWML | 1x8 排母 | `Conn_01x08` |
| XIO | 2x18 排母 | `Conn_02x18_Odd_Even` |

### 雜項
| BOM Ref | 元件 | **搜這個名字** |
|---|---|---|
| GROUND, RESET-EN | Solder jumper | `SolderJumper_2` |
| FD1–FD4 | Fiducial | `Fiducial_1mm` |

### 電源符號（不在 BOM，畫線時需要）
| 用途 | 名稱 |
|---|---|
| 5V 電源 | `PWR_5V` |
| 3.3V 電源 | `PWR_3V3` |
| GND | `PWR_GND` |
| VCC（USB 5V） | `VCC` |

### 搜尋技巧
1. 在 Eeschema 按 `A` 開啟 Add Symbol
2. 上方 Filter 輸入 `Arduino_Mega2560_Lib:` 只看本專案符號庫（共 31 個符號）
3. 從上表查到名字後直接搜（例如要 Polyfuse 就搜 `Fuse_1812`）

---

## Git 協作流程

### 初始設定

```bash
# 1. 先 fork 這個 repo 到你們組的帳號
# 2. Clone 到本機
git clone https://github.com/<你的組別>/kicad.git
cd kicad
```

### 每個人的工作流程

```bash
# 建立自己的 branch（以你負責的區塊命名）
git checkout -b section/01-usb-atmega16u2   # 依你的區塊修改

# 繪製原理圖後，只 commit 你負責的那個 .kicad_sch 檔
git add Arduino_Mega2560_Practice/Section_01_USB_ATmega16U2.kicad_sch
git commit -m "feat: complete USB ATmega16U2 section schematic"

# Push 到遠端
git push origin section/01-usb-atmega16u2

# 在 GitHub 發 Pull Request 給你們組的 main branch
```

### 合併注意事項

- 每個人只修改**自己負責的 `.kicad_sch` 檔**，不要動到其他人的檔案
- Root 主頁面 `Arduino_Mega2560_Practice.kicad_sch` 只有 4 個方框，不需要修改
- **不要 commit `.kicad_pcb`**（已被 `.gitignore` 排除），這個練習只做原理圖
- `*.bak`、`*.kicad_prl`、`*-backups/` 也都已被 ignore
- 合併後在 KiCad 開 `Arduino_Mega2560_Practice.kicad_pro` 即可看到完整原理圖
