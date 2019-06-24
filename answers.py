from engine.answershandler import AnswersHandler


def main():
    print('Answers processing starts')
    filename = "answers_1.txt"
    handler = AnswersHandler('./source/exp2')
    handler.read_file(filename)
    handler.set_subjects()
    handler.process_data()
    handler.write_result_as_csv('answers_agg_data.csv')
    print('Answers processing done')


if __name__ == "__main__":
    main()