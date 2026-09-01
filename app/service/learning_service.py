"""Business validation for dashboard, history and favorite-topic features."""

from app.models import learning_model


class LearningService:
    @staticmethod
    def dashboard(user_id):
        return learning_model.get_dashboard_summary(user_id)

    @staticmethod
    def save_submission(user_id, question_id, language, code, run_result, task_id=None):
        return learning_model.save_submission(user_id, question_id, language, code, run_result, task_id)

    @staticmethod
    def history(user_id, filters=None):
        return learning_model.get_submission_history(user_id, filters)

    @staticmethod
    def submission(user_id, submission_id):
        return learning_model.get_submission_detail(user_id, submission_id)

    @staticmethod
    def topics(user_id):
        return learning_model.list_topics(user_id)

    @staticmethod
    def create_topic(user_id, payload):
        name = str((payload or {}).get("name") or "").strip()
        if not 1 <= len(name) <= 80:
            raise ValueError("题单名称长度需为 1-80 个字符")
        return learning_model.create_topic(
            user_id, name,
            str((payload or {}).get("description") or "").strip()[:255],
            str((payload or {}).get("tags") or "").strip()[:255],
        )

    @staticmethod
    def update_topic(user_id, topic_id, payload):
        name = str((payload or {}).get("name") or "").strip()
        if not 1 <= len(name) <= 80:
            raise ValueError("题单名称长度需为 1-80 个字符")
        return learning_model.update_topic(
            user_id, topic_id, name,
            str((payload or {}).get("description") or "").strip()[:255],
            str((payload or {}).get("tags") or "").strip()[:255],
        )

    @staticmethod
    def delete_topic(user_id, topic_id):
        return learning_model.delete_topic(user_id, topic_id)

    @staticmethod
    def assign_topic(user_id, question_id, topic_id):
        return learning_model.assign_favorite_topic(user_id, question_id, topic_id)

    @staticmethod
    def save_draft(user_id, question_id, language, code):
        if question_id in (None, ""):
            raise ValueError("缺少题目 ID")
        if not isinstance(code, str) or len(code) > 200_000:
            raise ValueError("代码内容无效或超过 200KB")
        if language not in ("python", "javascript", "java", "c++", "cpp", "c"):
            raise ValueError("不支持的编程语言")
        return learning_model.save_draft(user_id, question_id, language, code)

    @staticmethod
    def draft(user_id, question_id):
        return learning_model.get_draft(user_id, question_id)
