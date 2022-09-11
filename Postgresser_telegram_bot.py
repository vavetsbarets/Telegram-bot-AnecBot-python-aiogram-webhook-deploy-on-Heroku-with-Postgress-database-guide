import psycopg2
import time

# This is the class with functions, which add/edit/delete information in the database
    # In the initialization of the class there is connection to the database!
    # And names of the methods of the class are basically explaining what they do

class Postgresser_general:
    def __init__(self, user, password, host, port, database):
        '''connect to database and save cursor connection'''
        self.connection = psycopg2.connect(user = user,
                                          password = password, 
                                          host = host, 
                                          port = port,
                                          database = database)
        self.cursor = self.connection.cursor()

        
    def add_feedback(self, user_id, date_feedback, rating, id_anec, is_present):
        '''adding user's feedback to the database'''
        if is_present == 0:
            self.cursor.execute("INSERT INTO users_history (user_id, date_feedback, rating, id_entry_from_general_base) VALUES (%s, %s, %s, %s)", (user_id, date_feedback, rating, id_anec))
        else:
            self.cursor.execute('UPDATE users_history SET rating = %s, date_feedback = %s WHERE user_id = %s AND id_entry_from_general_base = %s', (rating, date_feedback, user_id, id_anec))
           
        
    def add_user_to_users_sources(self, user_id):
        '''Adding user to the users_sources table with all 1, all sources chosen by default'''
        with self.connection:
        # write if user is not already in the table!!!!!
            self.cursor.execute('SELECT COUNT(*) FROM users_sources WHERE user_id = %s', (user_id,))
            d = self.cursor.fetchone()[0]
            if d == 0:
                self.cursor.execute("INSERT INTO users_sources (user_id, source_1_chosen, source_2_chosen, source_3_chosen, source_4_chosen, source_5_chosen, source_6_chosen, source_7_chosen, source_8_chosen, source_9_chosen, source_10_chosen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (user_id, bool(1), bool(1), bool(1), bool(1), bool(1), bool(1), bool(1), bool(1), bool(1), bool(1)))
    
    def add_user_to_users_sub_best_anec_day(self, user_id):
        '''User by default is subscribed to this feature'''
        with self.connection:
        # write if user is not already in the table!!!!!
            self.cursor.execute('SELECT COUNT(*) FROM users_sub_best_anec_day WHERE user_id = %s', (user_id,))
            d = self.cursor.fetchone()[0]
            if d == 0:
                self.cursor.execute("INSERT INTO users_sub_best_anec_day (user_id, subscribed) VALUES (%s, %s)", (user_id, bool(1)))
                
    def add_user_to_users_sub_random_anec(self, user_id):
        '''User by default is subscribed to this feature'''
        with self.connection:
        # write if user is not already in the table!!!!!
            self.cursor.execute('SELECT COUNT(*) FROM users_sub_random_anec WHERE user_id = %s', (user_id,))
            d = self.cursor.fetchone()[0]
            if d == 0:
                self.cursor.execute("INSERT INTO users_sub_random_anec (user_id, subscribed) VALUES (%s, %s)", (user_id, bool(1)))
        
    def delete_all_rows_of_feedbacks_for_one_user(self, user_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM users_history WHERE user_id = %s", (user_id,))
        
    def add_anec_to_main_base(self, row):
        with self.connection:
            self.cursor.execute("INSERT INTO anecdotes_general_table (id_prev_entry, id_prev_2_entry, id_anec, anec_text, date, source, target_group, source_id, part, cluster_inside, anec_cl, cluster_num) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]))
        
    def add_user_cluster_combination_to_users_clusters(self, user_id, cluster_num, anecs_read, average_rating, source_id, source_activated):
        with self.connection:
            self.cursor.execute("INSERT INTO users_clusters (user_id, cluster_num, anecs_read, average_rating, source_id, source_activated) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, cluster_num, anecs_read, average_rating, source_id, bool(source_activated)))
        
    def update_user_cluster_combination_in_users_clusters(self, id_entry, anecs_read, average_rating):
        with self.connection:
            self.cursor.execute("UPDATE users_clusters SET anecs_read = %s, average_rating = %s WHERE id_entry = %s", (anecs_read, average_rating, id_entry))
        
    def update_source_subscription_in_users_clusters(self, source_activated, user_id, source_id):
        with self.connection:
            self.cursor.execute("UPDATE users_clusters SET source_activated = %s WHERE user_id = %s AND source_id = %s", (bool(source_activated), user_id, source_id))
        
    def update_subscription_to_best_anec_day(self, user_id, subscribed):
        with self.connection:
            self.cursor.execute("UPDATE users_sub_best_anec_day SET subscribed = %s WHERE user_id = %s", (bool(subscribed), user_id))
            
    def update_subscription_to_random_anec(self, user_id, subscribed):
        with self.connection:
            self.cursor.execute("UPDATE users_sub_random_anec SET subscribed = %s WHERE user_id = %s", (bool(subscribed), user_id))
        
    def delete_all_rows_of_user_in_users_history_and_users_clusters_at_the_same_time(self, user_id):
        with self.connection:
            self.cursor.execute("DELETE FROM users_history WHERE user_id = %s", (user_id,))
            self.cursor.execute("DELETE FROM users_clusters WHERE user_id = %s", (user_id,))
            
    def add_anec_of_the_day_to_anec_of_day_table(self, id_anec, date, is_one_pretender):
        with self.connection:
            self.cursor.execute("INSERT INTO anec_of_day (unique_anec_id, win_day, is_one_pretender) VALUES (%s, %s, %s)", (id_anec, date, bool(is_one_pretender)))
            
    def add_message_id_to_two_tables_of_id_of_poll_message_by_day(self, date, id_message):
        with self.connection:
            self.cursor.execute("INSERT INTO id_of_poll_message_by_day_current (date, message_id) VALUES (%s, %s)", (date, id_message))
            self.cursor.execute("INSERT INTO id_of_poll_message_by_day_history (date, id_message) VALUES (%s, %s)", (date, id_message))
                        
    def delete_previous_message_id_from_id_of_poll_message_by_day_current(self):
        with self.connection:
            self.cursor.execute("DELETE FROM id_of_poll_message_by_day_current")
            
    def add_user_to_anecs_in_a_row_table(self, user_id):
        with self.connection:
            # write if user is not already in the table!!!!!
            self.cursor.execute('SELECT COUNT(*) FROM anecs_in_a_row WHERE user_id = %s', (user_id,))
            d = self.cursor.fetchone()[0]
            if d == 0:
                self.cursor.execute("INSERT INTO anecs_in_a_row (user_id, in_a_row_started) VALUES (%s, %s)", (user_id, bool(0)))
                
    def update_anecs_in_a_row_status(self, user_id, status):
        with self.connection:
            self.cursor.execute("UPDATE anecs_in_a_row SET in_a_row_started = %s WHERE user_id = %s", (bool(status), user_id))
        
    def add_anec_to_saved_anecs_by_user(self, user_id, id_anec, epoch_time_added):
        with self.connection:
            self.cursor.execute("INSERT INTO saved_anecs_by_user (user_id, id_anec, epoch_time_added, not_deleted) VALUES (%s, %s, %s, %s)", (user_id, id_anec, epoch_time_added, bool(1)))
        
    def update_status_of_saved_anec_and_add_or_remove_from_deleted_saved_table(self, user_id, id_anec, value):
        if value == 0:
            with self.connection:
                self.cursor.execute('UPDATE saved_anecs_by_user SET not_deleted = False WHERE user_id = %s AND id_anec = %s', (user_id, id_anec))
                self.cursor.execute('INSERT INTO saved_deleted_anecs_by_user (user_id, id_anec, epoch_time_deleted) VALUES (%s, %s, %s)', (user_id, id_anec, round(time.time())))
        elif value == 1:
            with self.connection:
                self.cursor.execute('UPDATE saved_anecs_by_user SET not_deleted = True WHERE user_id = %s AND id_anec = %s', (user_id, id_anec))
                self.cursor.execute('DELETE FROM saved_deleted_anecs_by_user WHERE user_id = %s AND id_anec = %s', (user_id, id_anec))
                
    def add_user_to_user_novice_or_not(self, user_id):
        '''Adding user to the users_sources table with all 1, all sources chosen by default'''
        with self.connection:
        # write if user is not already in the table!!!!!
            self.cursor.execute('SELECT COUNT(*) FROM user_novice_or_not WHERE user_id = %s', (user_id,))
            d = self.cursor.fetchone()[0]
            if d == 0:
                self.cursor.execute("INSERT INTO user_novice_or_not (user_id, is_novice) VALUES (%s, %s)", (user_id, True))
                
    def update_is_novice(self, user_id, is_novice):
        with self.connection:
            self.cursor.execute("UPDATE user_novice_or_not SET is_novice = %s WHERE user_id = %s", (bool(is_novice), user_id))
                
                
                
                
                
                