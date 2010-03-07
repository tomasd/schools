alter table courses_lesson add  "reason_of_not_realizing_id" integer;
CREATE INDEX "courses_lesson_reason_of_not_realizing_id" ON "courses_lesson" ("reason_of_not_realizing_id");
