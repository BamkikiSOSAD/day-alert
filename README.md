# Money Line Bot (Personal MVP)

บอทจดรายจ่ายส่วนตัวผ่าน LINE: พิมพ์อะไรก็ได้ “ขอมีเลข” แล้วระบบจะสรุปให้ทุกวันเวลา 20:00 (เวลาไทย) และเตือนตอน 12:00 ถ้ายังไม่จด

## ฟีเจอร์ (MVP)
- ตั้งงบรายวัน: พิมพ์ `งบ 300`
- จดรายจ่าย: พิมพ์อะไรก็ได้ที่มีเลข เช่น `กาแฟ 60`, `-120 ข้าว`
- สรุปอัตโนมัติทุกวัน 20:00 (เวลาไทย)
- เตือนอัตโนมัติทุกวัน 12:00 (เวลาไทย) ถ้ายังไม่มีรายการวันนี้

## โครงสร้าง
- `data/today.json` เก็บ state ของ “วันนี้” (วันเดียว) — MVP เน้นใช้คนเดียวก่อน
- GitHub Actions ทำงานตามเวลา (cron เป็น UTC)
- Webhook receiver (แนะนำ Cloudflare Worker) รับข้อความจาก LINE แล้วอัปเดต `today.json` ใน repo ผ่าน GitHub API

## ตั้งค่า Secrets (GitHub)
ไปที่ Repo → Settings → Secrets and variables → Actions → New repository secret

### LINE
- `LINE_CHANNEL_ACCESS_TOKEN` : Channel access token (Messaging API)
- `LINE_USER_ID` : User ID ที่จะส่งข้อความกลับ (ใช้คนเดียวก่อน)

### GitHub (สำหรับ webhook receiver ที่จะ commit เข้า repo)
- `GH_PAT` : Personal Access Token ที่มีสิทธิ์ `repo` (private) หรือ `public_repo` (public)

> หมายเหตุ: GH_PAT ไม่จำเป็นสำหรับ workflow สรุป/เตือน (เพราะ workflow ใช้ไฟล์ใน repo อยู่แล้ว)  
> GH_PAT ใช้เฉพาะ “ตัวรับ webhook” ที่จะเขียนไฟล์กลับเข้า repo

## เวลา Cron (สำคัญ)
GitHub Actions cron ใช้ **UTC**
- 12:00 (เวลาไทย, ICT=UTC+7) = **05:00 UTC**
- 20:00 (เวลาไทย) = **13:00 UTC**

ไฟล์ workflow ตั้งไว้ให้แล้ว

## การใช้งาน (ฝั่งผู้ใช้)
- ตั้งงบ: `งบ 300`
- จด: `กาแฟ 60` หรือ `-120 ข้าว`
- ล้างรายการวันนี้: `ล้าง` (จะเคลียร์ items แต่ไม่ล้าง budget)

## แนะนำ webhook receiver
ดูโฟลเดอร์ `webhook_receiver/`:
- `cloudflare_worker.js` (แนะนำ)
- `local_flask_receiver.py` (สำหรับเทส local)

คุณต้องตั้ง LINE webhook URL ให้ชี้ไปที่ receiver ของคุณ

---
## ข้อจำกัด MVP
- เก็บแค่ “วันปัจจุบัน” ใน `today.json`
- ยังไม่รองรับหลาย user (จะทำต่อได้ โดยแยกไฟล์ตาม user_id)
