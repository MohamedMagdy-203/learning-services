from typing import List, Dict, Any


class SessionAnalytics:
    @staticmethod
    def total_answered(history: List[Dict[str, Any]]) -> int:
        return len(history)

    @staticmethod
    def recent_answers(history: List[Dict[str, Any]], count: int = 5):
        return history[-count:]

    @classmethod
    def recent_accuracy(cls, history, count=5):
        recent = cls.recent_answers(history, count)
        if not recent:
            return 0.0
        return sum(1 for r in recent if r["is_correct"]) / len(recent)

    @staticmethod
    def consecutive_correct(history):
        streak = 0
        for h in reversed(history):
            if h["is_correct"]:
                streak += 1
            else:
                break
        return streak

    @staticmethod
    def consecutive_wrong(history):
        streak = 0
        for h in reversed(history):
            if not h["is_correct"]:
                streak += 1
            else:
                break
        return streak

    @classmethod
    def consistency_score(cls, history):
        recent = cls.recent_answers(history, 5)
        if len(recent) < 3:
            return 0.3

        values = [1 if r["is_correct"] else 0 for r in recent]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)

        return max(0.0, min(1 - variance, 1.0))

    @staticmethod
    def question_count_score(total_answered: int, max_questions: int):
        return min(total_answered / max_questions, 1.0)

    @staticmethod
    def speed_score(history: List[Dict[str, Any]]) -> float:
        if not history:
            return 0.5

        recent = history[-5:]

        expected_time_map = {"easy": 20, "medium": 30, "hard": 45}

        scores = []

        for h in recent:
            difficulty = h.get("difficulty", "medium")
            expected_time = expected_time_map.get(difficulty, 30)

            actual_time = h["response_time"]
            ratio = actual_time / expected_time

            if ratio <= 0.8:
                score = 1.0
            elif ratio <= 1.0:
                score = 0.8
            elif ratio <= 1.2:
                score = 0.6
            elif ratio <= 1.5:
                score = 0.4
            else:
                score = 0.2

            scores.append(score)

        return sum(scores) / len(scores)
