# 🧪 ADAPTIVE LEARNING - MANUAL TESTING GUIDE

## 📋 **PREREQUISITES**

1. **Start MongoDB**
   ```bash
   # Make sure MongoDB is running on localhost:27017
   ```

2. **Start Backend Server**
   ```bash
   cd BELEARNINGAI
   uvicorn app.main:app --reload
   ```

3. **Open Swagger UI**
   ```
   http://localhost:8000/docs
   ```

---

## 🎯 **TEST SCENARIO: COMPLETE ADAPTIVE LEARNING FLOW**

### **Step 1: Register & Login** 🔐

#### **1.1 Register a Student**
- Endpoint: `POST /api/v1/auth/register`
- Payload:
```json
{
  "full_name": "Test Student",
  "email": "teststudent@example.com",
  "password": "Test@12345"
}
```
- Expected: `201 Created`

#### **1.2 Login**
- Endpoint: `POST /api/v1/auth/login`
- Payload:
```json
{
  "email": "teststudent@example.com",
  "password": "Test@12345",
  "remember_me": false
}
```
- Expected: `200 OK`
- **SAVE:** `access_token` from response

#### **1.3 Authorize in Swagger**
- Click **"Authorize"** button (top right)
- Enter: `Bearer <your_access_token>`
- Click **"Authorize"**

---

### **Step 2: Create Course & Enrollment** 📚

#### **2.1 Get Available Courses**
- Endpoint: `GET /api/v1/courses`
- Expected: List of courses
- **SAVE:** `course_id` from any course

#### **2.2 Enroll in Course**
- Endpoint: `POST /api/v1/enrollments`
- Payload:
```json
{
  "course_id": "<course_id_from_step_2.1>"
}
```
- Expected: `201 Created`
- **SAVE:** `enrollment_id` from response

---

### **Step 3: Complete Assessment** 📝

#### **3.1 Start Assessment**
- Endpoint: `POST /api/v1/assessments/start`
- Payload:
```json
{
  "course_id": "<course_id>"
}
```
- Expected: `200 OK`
- **SAVE:** `assessment_session_id`

#### **3.2 Submit Assessment**
- Endpoint: `POST /api/v1/assessments/{assessment_session_id}/submit`
- Payload:
```json
{
  "answers": [
    {"question_id": "q1", "answer": "A"},
    {"question_id": "q2", "answer": "B"}
  ]
}
```
- Expected: `200 OK`
- **SAVE:** `score` (should be >= 85% for auto-skip)

---

### **Step 4: TEST FEATURE 1 - Auto-Skip Module** 🚀

#### **4.1 Apply Assessment to Enrollment**
- Endpoint: `POST /api/v1/adaptive-learning/apply-assessment`
- Payload:
```json
{
  "assessment_session_id": "<assessment_session_id>",
  "course_id": "<course_id>",
  "enrollment_id": "<enrollment_id>",
  "skip_threshold": 0.85,
  "time_threshold": 0.50
}
```

#### **Expected Response:**
```json
{
  "success": true,
  "message": "Assessment applied successfully",
  "data": {
    "skipped_modules": [
      {
        "module_id": "...",
        "module_title": "...",
        "reason": "High assessment score (90%) and fast completion"
      }
    ],
    "recommended_start_module_id": "...",
    "new_progress_percent": 25.0,
    "time_saved_hours": 2.5
  }
}
```

#### **Verify:**
- ✅ `skipped_modules` array is not empty (if score >= 85%)
- ✅ `recommended_start_module_id` is set
- ✅ `new_progress_percent` > 0
- ✅ `time_saved_hours` > 0

---

### **Step 5: TEST FEATURE 2 - Adaptive Learning Path** 🎯

#### **5.1 Create Adaptive Path**
- Endpoint: `POST /api/v1/adaptive-learning/create-adaptive-path`
- Payload:
```json
{
  "assessment_session_id": "<assessment_session_id>",
  "course_id": "<course_id>",
  "enrollment_id": "<enrollment_id>"
}
```

#### **Expected Response:**
```json
{
  "success": true,
  "message": "Adaptive learning path created",
  "data": {
    "adaptive_path": [
      {
        "module_id": "...",
        "module_title": "...",
        "decision": "SKIP",
        "reason": "Strong proficiency (95%) - Skip recommended",
        "proficiency_score": 95.0
      },
      {
        "module_id": "...",
        "module_title": "...",
        "decision": "START",
        "reason": "Moderate proficiency (70%) - Start here",
        "proficiency_score": 70.0
      }
    ],
    "total_modules": 5,
    "skip_count": 2,
    "review_count": 1,
    "start_count": 2
  }
}
```

#### **Verify:**
- ✅ `adaptive_path` has 5 decision types: SKIP, REVIEW, START, UNLOCK, LOCKED
- ✅ Each module has: `decision`, `reason`, `proficiency_score`
- ✅ Counts match: `skip_count + review_count + start_count + unlock_count + locked_count = total_modules`

---

### **Step 6: TEST FEATURE 3 - Continuous Adjustment** ⚡

#### **6.1 Track Lesson Completion (Fast Learner)**
- Endpoint: `POST /api/v1/adaptive-learning/track-completion`
- Payload:
```json
{
  "course_id": "<course_id>",
  "lesson_id": "<lesson_id>",
  "time_spent_seconds": 600,
  "quiz_score": 95.0,
  "attempts": 1
}
```

#### **Expected Response (Fast Learner):**
```json
{
  "success": true,
  "message": "Completion tracked",
  "adjustment": {
    "adjustment_needed": true,
    "adjustment_type": "SPEED_UP",
    "suggestion": {
      "message": "You're learning faster than expected!",
      "action": "skip_next_lessons",
      "lessons_to_skip": ["lesson_2", "lesson_3"]
    }
  }
}
```

#### **6.2 Track Lesson Completion (Slow Learner)**
- Payload:
```json
{
  "course_id": "<course_id>",
  "lesson_id": "<lesson_id>",
  "time_spent_seconds": 7200,
  "quiz_score": 55.0,
  "attempts": 3
}
```

#### **Expected Response (Slow Learner):**
```json
{
  "success": true,
  "message": "Completion tracked",
  "adjustment": {
    "adjustment_needed": true,
    "adjustment_type": "REVIEW",
    "suggestion": {
      "message": "Consider reviewing prerequisite lessons",
      "action": "review_lessons",
      "lessons_to_review": ["lesson_1"]
    }
  }
}
```

#### **Verify:**
- ✅ Fast learner → `adjustment_type` = "SPEED_UP"
- ✅ Slow learner → `adjustment_type` = "REVIEW" or "SCHEDULE"
- ✅ Suggestion includes actionable message

---

### **Step 7: Get Adaptive Info** 📊

#### **7.1 Get Enrollment Adaptive Info**
- Endpoint: `GET /api/v1/adaptive-learning/enrollment/{enrollment_id}/adaptive-info`

#### **Expected Response:**
```json
{
  "success": true,
  "data": {
    "adaptive_learning_enabled": true,
    "skipped_modules": [...],
    "recommended_start_module_id": "...",
    "learning_path_decisions": [...],
    "current_adjustment": {...}
  }
}
```

---

### **Step 8: Accept Adjustment** ✅

#### **8.1 Accept Suggested Adjustment**
- Endpoint: `POST /api/v1/adaptive-learning/enrollment/{enrollment_id}/accept-adjustment`
- Payload:
```json
{
  "adjustment_type": "SPEED_UP",
  "accepted": true
}
```

#### **Expected Response:**
```json
{
  "success": true,
  "message": "Adjustment accepted and applied"
}
```

---

## ✅ **SUCCESS CRITERIA**

All features working if:
- ✅ Auto-skip works for high scores (>= 85%)
- ✅ Adaptive path shows 5 decision types
- ✅ Fast learner gets SPEED_UP adjustment
- ✅ Slow learner gets REVIEW adjustment
- ✅ Get adaptive info returns correct data
- ✅ Accept adjustment updates enrollment

---

## 📝 **NOTES**

- All endpoints require authentication (Bearer token)
- Assessment score >= 85% triggers auto-skip
- Time < 50% of expected triggers speed-up
- Score < 70% triggers review suggestions

---

**Last Updated:** 2024-12-25

