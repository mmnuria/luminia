# Luminia
**Author:** Nuria Manzano Mata. 

**Final Degree Project – Bachelor’s in Computer Engineering**. The final grade obtained was a 10 (with highest honors).

**Luminia** is an educational application aimed at children aged 4 to 6, designed to support the learning of basic concepts while developing cognitive and motor skills. The application combines augmented reality, implicit interaction, context awareness, and gamification, providing an engaging and interactive experience in themed worlds guided by the character Tina.

---

## Purpose

The goal of Luminia is to provide a safe and educational environment where children can learn while playing. Through progressive challenges and visual rewards, the application aims to enhance attention, memory, coordination, and motivation in young learners.

---

## Requirements

- Python 3.10 or higher  
- [Docker](https://www.docker.com/) (for MongoDB database)  
- Python dependencies listed in `requirements.txt`  
- Webcam (for calibration and AR activities)

---

## Installation and Running

1. **Create a virtual environment (optional but recommended):**
```bash
python3 -m venv luminia_env
source luminia_env/bin/activate
```
2. **Clone the repository:**
```bash
git clone https://github.com/mmnuria/luminia.git
cd luminia
```
3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Calibrate the camera:**

Print the calibration pattern config/charuco.tiff.

Run:
```bash
python calibrar_camara.py
```

Keep the board visible in front of the camera. The application will show how many images have been captured. Press ESC to finish before the maximum number of captures.

After completion, camara.py will be automatically generated with the calibration parameters.

5. **Start MongoDB using Docker:**
```bash
docker run -d -p 27017:27017 \
-e MONGO_INITDB_ROOT_USERNAME=root \
-e MONGO_INITDB_ROOT_PASSWORD=example \
mongo
```

6. **Run the application:**
```bash
python main.py
```

# License

This project is licensed under the Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).

