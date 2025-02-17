PGDMP     '    6        
        }            nalib_db     15.10 (Debian 15.10-1.pgdg120+1)     15.10 (Debian 15.10-1.pgdg120+1) \    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    16384    nalib_db    DATABASE     s   CREATE DATABASE nalib_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';
    DROP DATABASE nalib_db;
             	   thokozani    false            �            1255    16670    generate_admin_notification()    FUNCTION     �  CREATE FUNCTION public.generate_admin_notification() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            -- Insert notification based on whether it's a member or staff
            IF (TG_TABLE_NAME = 'members') THEN
                INSERT INTO notifications (message, member_id, role, created_at)
                VALUES ('A new record has been added to ' || TG_TABLE_NAME, NEW.member_id, 'Member', NOW());
   
            ELSIF (TG_TABLE_NAME = 'staff') THEN
                INSERT INTO notifications (message, staff_id, role, created_at)
                VALUES ('A new record has been added to ' || TG_TABLE_NAME, NEW.id, 'Staff', NOW());
            END IF;
        ELSIF (TG_OP = 'UPDATE') THEN
            -- Insert notification based on whether it's a member or staff
            IF (TG_TABLE_NAME = 'members') THEN
                INSERT INTO notifications (message, member_id, role, created_at)
                VALUES ('A record has been updated in ' || TG_TABLE_NAME, NEW.id, 'Member', NOW());
            ELSIF (TG_TABLE_NAME = 'staff') THEN
                INSERT INTO notifications (message, staff_id, role, created_at)
                VALUES ('A record has been updated in ' || TG_TABLE_NAME, NEW.id, 'Staff', NOW());
            END IF;
        ELSIF (TG_OP = 'DELETE') THEN
            -- Insert notification based on whether it's a member or staff
            IF (TG_TABLE_NAME = 'members') THEN
                INSERT INTO notifications (message, member_id, role, created_at)
                VALUES ('A record has been deleted from ' || TG_TABLE_NAME, OLD.id, 'Member', NOW());
            ELSIF (TG_TABLE_NAME = 'staff') THEN
                INSERT INTO notifications (message, staff_id, role, created_at)
                VALUES ('A record has been deleted from ' || TG_TABLE_NAME, OLD.id, 'Staff', NOW());
            END IF;
        END IF;
        RETURN NULL;
    END;
    $$;
 4   DROP FUNCTION public.generate_admin_notification();
       public       	   thokozani    false            �            1259    16529    borrowing_rules    TABLE     �  CREATE TABLE public.borrowing_rules (
    rule_id integer NOT NULL,
    resource_type character varying(50),
    max_borrow_duration integer,
    reminder_intervals json,
    CONSTRAINT check_max_borrow_duration_positive CHECK ((max_borrow_duration > 0)),
    CONSTRAINT check_resource_type_valid CHECK (((resource_type)::text = ANY ((ARRAY['book'::character varying, 'newspaper'::character varying, 'article'::character varying])::text[])))
);
 #   DROP TABLE public.borrowing_rules;
       public         heap 	   thokozani    false            �            1259    16528    borrowing_rules_rule_id_seq    SEQUENCE     �   CREATE SEQUENCE public.borrowing_rules_rule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.borrowing_rules_rule_id_seq;
       public       	   thokozani    false    219            �           0    0    borrowing_rules_rule_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.borrowing_rules_rule_id_seq OWNED BY public.borrowing_rules.rule_id;
          public       	   thokozani    false    218            �            1259    16520    genres    TABLE     n   CREATE TABLE public.genres (
    genre_id integer NOT NULL,
    genre_name character varying(100) NOT NULL
);
    DROP TABLE public.genres;
       public         heap 	   thokozani    false            �            1259    16519    genres_genre_id_seq    SEQUENCE     �   CREATE SEQUENCE public.genres_genre_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.genres_genre_id_seq;
       public       	   thokozani    false    217            �           0    0    genres_genre_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public.genres_genre_id_seq OWNED BY public.genres.genre_id;
          public       	   thokozani    false    216            �            1259    17441    lending_transactions    TABLE     i  CREATE TABLE public.lending_transactions (
    transaction_id integer NOT NULL,
    member_id integer,
    resource_id integer,
    borrowed_on timestamp without time zone,
    due_date timestamp without time zone NOT NULL,
    returned_on timestamp without time zone,
    return_date timestamp without time zone,
    status character varying(20),
    condition_on_return character varying(20),
    staff_id integer,
    reward_points integer,
    CONSTRAINT check_condition_on_return_valid CHECK (((condition_on_return)::text = ANY ((ARRAY['good'::character varying, 'damaged'::character varying, 'lost'::character varying])::text[]))),
    CONSTRAINT check_status_valid CHECK (((status)::text = ANY ((ARRAY['borrowed'::character varying, 'returned'::character varying, 'overdue'::character varying, 'damaged'::character varying, 'lost'::character varying])::text[])))
);
 (   DROP TABLE public.lending_transactions;
       public         heap 	   thokozani    false            �            1259    17440 '   lending_transactions_transaction_id_seq    SEQUENCE     �   CREATE SEQUENCE public.lending_transactions_transaction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 >   DROP SEQUENCE public.lending_transactions_transaction_id_seq;
       public       	   thokozani    false    231            �           0    0 '   lending_transactions_transaction_id_seq    SEQUENCE OWNED BY     s   ALTER SEQUENCE public.lending_transactions_transaction_id_seq OWNED BY public.lending_transactions.transaction_id;
          public       	   thokozani    false    230            �            1259    16630    library_resources    TABLE     )  CREATE TABLE public.library_resources (
    resource_id integer NOT NULL,
    title character varying(255) NOT NULL,
    author character varying(255),
    genre_id integer,
    resource_type character varying(50),
    format character varying(50),
    available boolean,
    location character varying(255),
    added_by_staff_id integer,
    added_on timestamp without time zone,
    items integer NOT NULL,
    CONSTRAINT check_format_valid CHECK (((format)::text = ANY ((ARRAY['hardcopy'::character varying, 'electronic'::character varying])::text[]))),
    CONSTRAINT check_items_non_negative CHECK ((items >= 0)),
    CONSTRAINT check_resource_type_valid CHECK (((resource_type)::text = ANY ((ARRAY['book'::character varying, 'newspaper'::character varying, 'article'::character varying])::text[])))
);
 %   DROP TABLE public.library_resources;
       public         heap 	   thokozani    false            �            1259    16540    members    TABLE     R  CREATE TABLE public.members (
    member_id integer NOT NULL,
    membership_number character varying(50) NOT NULL,
    name character varying(255) NOT NULL,
    address json,
    email character varying(255),
    phone character varying(20),
    enrolled_on timestamp without time zone,
    status character varying(20),
    borrowing_behavior json,
    password_hash text DEFAULT 'default_hash'::text NOT NULL,
    CONSTRAINT check_status_valid CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'suspended'::character varying, 'deactivated'::character varying])::text[])))
);
    DROP TABLE public.members;
       public         heap 	   thokozani    false            �            1259    17860    library_reports    VIEW     �  CREATE VIEW public.library_reports AS
 SELECT 1 AS dummy_id,
    ( SELECT count(*) AS count
           FROM public.library_resources) AS total_resources,
    ( SELECT count(*) AS count
           FROM public.members) AS total_members,
    ( SELECT count(*) AS count
           FROM public.lending_transactions
          WHERE ((lending_transactions.status)::text = 'borrowed'::text)) AS total_borrowed_resources,
    ( SELECT count(*) AS count
           FROM public.lending_transactions
          WHERE ((lending_transactions.due_date < now()) AND ((lending_transactions.status)::text = 'borrowed'::text))) AS overdue_transactions,
    ( SELECT count(*) AS count
           FROM public.genres) AS total_genres,
    ( SELECT count(*) AS count
           FROM public.lending_transactions
          WHERE ((lending_transactions.returned_on IS NULL) AND (lending_transactions.due_date < now()))) AS overdue_returns,
    ( SELECT avg(subquery.borrow_count) AS avg
           FROM ( SELECT count(*) AS borrow_count
                   FROM public.lending_transactions
                  GROUP BY lending_transactions.member_id) subquery) AS avg_borrowed_per_member;
 "   DROP VIEW public.library_reports;
       public       	   thokozani    false    231    217    221    227    231    231    231            �            1259    16629 !   library_resources_resource_id_seq    SEQUENCE     �   CREATE SEQUENCE public.library_resources_resource_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 8   DROP SEQUENCE public.library_resources_resource_id_seq;
       public       	   thokozani    false    227            �           0    0 !   library_resources_resource_id_seq    SEQUENCE OWNED BY     g   ALTER SEQUENCE public.library_resources_resource_id_seq OWNED BY public.library_resources.resource_id;
          public       	   thokozani    false    226            �            1259    16539    members_member_id_seq    SEQUENCE     �   CREATE SEQUENCE public.members_member_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public.members_member_id_seq;
       public       	   thokozani    false    221            �           0    0    members_member_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public.members_member_id_seq OWNED BY public.members.member_id;
          public       	   thokozani    false    220            �            1259    16780    notifications    TABLE     �  CREATE TABLE public.notifications (
    id integer NOT NULL,
    message character varying(255) NOT NULL,
    member_id integer,
    staff_id integer,
    role character varying(50) NOT NULL,
    seen boolean,
    created_at timestamp without time zone,
    CONSTRAINT check_role_valid CHECK (((role)::text = ANY ((ARRAY['Admin'::character varying, 'Staff'::character varying, 'Member'::character varying])::text[])))
);
 !   DROP TABLE public.notifications;
       public         heap 	   thokozani    false            �            1259    16779    notifications_id_seq    SEQUENCE     �   CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.notifications_id_seq;
       public       	   thokozani    false    229            �           0    0    notifications_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;
          public       	   thokozani    false    228            �            1259    16616    password_policies    TABLE     �   CREATE TABLE public.password_policies (
    policy_id integer NOT NULL,
    user_id integer,
    last_changed timestamp without time zone,
    expires_after interval
);
 %   DROP TABLE public.password_policies;
       public         heap 	   thokozani    false            �            1259    16615    password_policies_policy_id_seq    SEQUENCE     �   CREATE SEQUENCE public.password_policies_policy_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 6   DROP SEQUENCE public.password_policies_policy_id_seq;
       public       	   thokozani    false    225            �           0    0    password_policies_policy_id_seq    SEQUENCE OWNED BY     c   ALTER SEQUENCE public.password_policies_policy_id_seq OWNED BY public.password_policies.policy_id;
          public       	   thokozani    false    224            �            1259    16510    staff    TABLE     �  CREATE TABLE public.staff (
    staff_id integer NOT NULL,
    name character varying(255) NOT NULL,
    qualification text,
    experience text,
    skill_set text,
    grade character varying(50),
    contact_info json,
    role character varying(50),
    status boolean,
    CONSTRAINT check_role_valid CHECK (((role)::text = ANY ((ARRAY['Admin'::character varying, 'Staff'::character varying, 'Member'::character varying])::text[])))
);
    DROP TABLE public.staff;
       public         heap 	   thokozani    false            �            1259    16509    staff_staff_id_seq    SEQUENCE     �   CREATE SEQUENCE public.staff_staff_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.staff_staff_id_seq;
       public       	   thokozani    false    215            �           0    0    staff_staff_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public.staff_staff_id_seq OWNED BY public.staff.staff_id;
          public       	   thokozani    false    214            �            1259    16575 
   user_roles    TABLE     B  CREATE TABLE public.user_roles (
    user_id integer NOT NULL,
    staff_id integer,
    role character varying(50),
    password_hash text NOT NULL,
    CONSTRAINT user_roles_role_check CHECK (((role)::text = ANY ((ARRAY['Admin'::character varying, 'Staff'::character varying, 'Member'::character varying])::text[])))
);
    DROP TABLE public.user_roles;
       public         heap 	   thokozani    false            �            1259    16574    user_roles_user_id_seq    SEQUENCE     �   CREATE SEQUENCE public.user_roles_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.user_roles_user_id_seq;
       public       	   thokozani    false    223            �           0    0    user_roles_user_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.user_roles_user_id_seq OWNED BY public.user_roles.user_id;
          public       	   thokozani    false    222            �           2604    16532    borrowing_rules rule_id    DEFAULT     �   ALTER TABLE ONLY public.borrowing_rules ALTER COLUMN rule_id SET DEFAULT nextval('public.borrowing_rules_rule_id_seq'::regclass);
 F   ALTER TABLE public.borrowing_rules ALTER COLUMN rule_id DROP DEFAULT;
       public       	   thokozani    false    218    219    219            �           2604    16523    genres genre_id    DEFAULT     r   ALTER TABLE ONLY public.genres ALTER COLUMN genre_id SET DEFAULT nextval('public.genres_genre_id_seq'::regclass);
 >   ALTER TABLE public.genres ALTER COLUMN genre_id DROP DEFAULT;
       public       	   thokozani    false    216    217    217            �           2604    17444 #   lending_transactions transaction_id    DEFAULT     �   ALTER TABLE ONLY public.lending_transactions ALTER COLUMN transaction_id SET DEFAULT nextval('public.lending_transactions_transaction_id_seq'::regclass);
 R   ALTER TABLE public.lending_transactions ALTER COLUMN transaction_id DROP DEFAULT;
       public       	   thokozani    false    231    230    231            �           2604    16633    library_resources resource_id    DEFAULT     �   ALTER TABLE ONLY public.library_resources ALTER COLUMN resource_id SET DEFAULT nextval('public.library_resources_resource_id_seq'::regclass);
 L   ALTER TABLE public.library_resources ALTER COLUMN resource_id DROP DEFAULT;
       public       	   thokozani    false    227    226    227            �           2604    16543    members member_id    DEFAULT     v   ALTER TABLE ONLY public.members ALTER COLUMN member_id SET DEFAULT nextval('public.members_member_id_seq'::regclass);
 @   ALTER TABLE public.members ALTER COLUMN member_id DROP DEFAULT;
       public       	   thokozani    false    221    220    221            �           2604    16783    notifications id    DEFAULT     t   ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);
 ?   ALTER TABLE public.notifications ALTER COLUMN id DROP DEFAULT;
       public       	   thokozani    false    229    228    229            �           2604    16619    password_policies policy_id    DEFAULT     �   ALTER TABLE ONLY public.password_policies ALTER COLUMN policy_id SET DEFAULT nextval('public.password_policies_policy_id_seq'::regclass);
 J   ALTER TABLE public.password_policies ALTER COLUMN policy_id DROP DEFAULT;
       public       	   thokozani    false    225    224    225            �           2604    16513    staff staff_id    DEFAULT     p   ALTER TABLE ONLY public.staff ALTER COLUMN staff_id SET DEFAULT nextval('public.staff_staff_id_seq'::regclass);
 =   ALTER TABLE public.staff ALTER COLUMN staff_id DROP DEFAULT;
       public       	   thokozani    false    215    214    215            �           2604    16578    user_roles user_id    DEFAULT     x   ALTER TABLE ONLY public.user_roles ALTER COLUMN user_id SET DEFAULT nextval('public.user_roles_user_id_seq'::regclass);
 A   ALTER TABLE public.user_roles ALTER COLUMN user_id DROP DEFAULT;
       public       	   thokozani    false    222    223    223            �          0    16529    borrowing_rules 
   TABLE DATA           j   COPY public.borrowing_rules (rule_id, resource_type, max_borrow_duration, reminder_intervals) FROM stdin;
    public       	   thokozani    false    219   Ɋ       �          0    16520    genres 
   TABLE DATA           6   COPY public.genres (genre_id, genre_name) FROM stdin;
    public       	   thokozani    false    217   �       �          0    17441    lending_transactions 
   TABLE DATA           �   COPY public.lending_transactions (transaction_id, member_id, resource_id, borrowed_on, due_date, returned_on, return_date, status, condition_on_return, staff_id, reward_points) FROM stdin;
    public       	   thokozani    false    231   J�       �          0    16630    library_resources 
   TABLE DATA           �   COPY public.library_resources (resource_id, title, author, genre_id, resource_type, format, available, location, added_by_staff_id, added_on, items) FROM stdin;
    public       	   thokozani    false    227   ��       �          0    16540    members 
   TABLE DATA           �   COPY public.members (member_id, membership_number, name, address, email, phone, enrolled_on, status, borrowing_behavior, password_hash) FROM stdin;
    public       	   thokozani    false    221   ��       �          0    16780    notifications 
   TABLE DATA           a   COPY public.notifications (id, message, member_id, staff_id, role, seen, created_at) FROM stdin;
    public       	   thokozani    false    229   �       �          0    16616    password_policies 
   TABLE DATA           \   COPY public.password_policies (policy_id, user_id, last_changed, expires_after) FROM stdin;
    public       	   thokozani    false    225   ��                 0    16510    staff 
   TABLE DATA           x   COPY public.staff (staff_id, name, qualification, experience, skill_set, grade, contact_info, role, status) FROM stdin;
    public       	   thokozani    false    215   ��       �          0    16575 
   user_roles 
   TABLE DATA           L   COPY public.user_roles (user_id, staff_id, role, password_hash) FROM stdin;
    public       	   thokozani    false    223   .�       �           0    0    borrowing_rules_rule_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.borrowing_rules_rule_id_seq', 4, true);
          public       	   thokozani    false    218            �           0    0    genres_genre_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.genres_genre_id_seq', 2, true);
          public       	   thokozani    false    216            �           0    0 '   lending_transactions_transaction_id_seq    SEQUENCE SET     U   SELECT pg_catalog.setval('public.lending_transactions_transaction_id_seq', 4, true);
          public       	   thokozani    false    230            �           0    0 !   library_resources_resource_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.library_resources_resource_id_seq', 2, true);
          public       	   thokozani    false    226            �           0    0    members_member_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.members_member_id_seq', 8, true);
          public       	   thokozani    false    220            �           0    0    notifications_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.notifications_id_seq', 2, true);
          public       	   thokozani    false    228            �           0    0    password_policies_policy_id_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('public.password_policies_policy_id_seq', 1, false);
          public       	   thokozani    false    224            �           0    0    staff_staff_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.staff_staff_id_seq', 2, true);
          public       	   thokozani    false    214            �           0    0    user_roles_user_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.user_roles_user_id_seq', 2, true);
          public       	   thokozani    false    222            �           2606    16538 $   borrowing_rules borrowing_rules_pkey 
   CONSTRAINT     g   ALTER TABLE ONLY public.borrowing_rules
    ADD CONSTRAINT borrowing_rules_pkey PRIMARY KEY (rule_id);
 N   ALTER TABLE ONLY public.borrowing_rules DROP CONSTRAINT borrowing_rules_pkey;
       public         	   thokozani    false    219            �           2606    16527    genres genres_genre_name_key 
   CONSTRAINT     ]   ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_genre_name_key UNIQUE (genre_name);
 F   ALTER TABLE ONLY public.genres DROP CONSTRAINT genres_genre_name_key;
       public         	   thokozani    false    217            �           2606    16525    genres genres_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_pkey PRIMARY KEY (genre_id);
 <   ALTER TABLE ONLY public.genres DROP CONSTRAINT genres_pkey;
       public         	   thokozani    false    217            �           2606    17448 .   lending_transactions lending_transactions_pkey 
   CONSTRAINT     x   ALTER TABLE ONLY public.lending_transactions
    ADD CONSTRAINT lending_transactions_pkey PRIMARY KEY (transaction_id);
 X   ALTER TABLE ONLY public.lending_transactions DROP CONSTRAINT lending_transactions_pkey;
       public         	   thokozani    false    231            �           2606    16640 (   library_resources library_resources_pkey 
   CONSTRAINT     o   ALTER TABLE ONLY public.library_resources
    ADD CONSTRAINT library_resources_pkey PRIMARY KEY (resource_id);
 R   ALTER TABLE ONLY public.library_resources DROP CONSTRAINT library_resources_pkey;
       public         	   thokozani    false    227            �           2606    16552    members members_email_key 
   CONSTRAINT     U   ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_email_key UNIQUE (email);
 C   ALTER TABLE ONLY public.members DROP CONSTRAINT members_email_key;
       public         	   thokozani    false    221            �           2606    16550 %   members members_membership_number_key 
   CONSTRAINT     m   ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_membership_number_key UNIQUE (membership_number);
 O   ALTER TABLE ONLY public.members DROP CONSTRAINT members_membership_number_key;
       public         	   thokozani    false    221            �           2606    16548    members members_pkey 
   CONSTRAINT     Y   ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_pkey PRIMARY KEY (member_id);
 >   ALTER TABLE ONLY public.members DROP CONSTRAINT members_pkey;
       public         	   thokozani    false    221            �           2606    16786     notifications notifications_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.notifications DROP CONSTRAINT notifications_pkey;
       public         	   thokozani    false    229            �           2606    16621 (   password_policies password_policies_pkey 
   CONSTRAINT     m   ALTER TABLE ONLY public.password_policies
    ADD CONSTRAINT password_policies_pkey PRIMARY KEY (policy_id);
 R   ALTER TABLE ONLY public.password_policies DROP CONSTRAINT password_policies_pkey;
       public         	   thokozani    false    225            �           2606    16623 /   password_policies password_policies_user_id_key 
   CONSTRAINT     m   ALTER TABLE ONLY public.password_policies
    ADD CONSTRAINT password_policies_user_id_key UNIQUE (user_id);
 Y   ALTER TABLE ONLY public.password_policies DROP CONSTRAINT password_policies_user_id_key;
       public         	   thokozani    false    225            �           2606    16518    staff staff_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_pkey PRIMARY KEY (staff_id);
 :   ALTER TABLE ONLY public.staff DROP CONSTRAINT staff_pkey;
       public         	   thokozani    false    215            �           2606    16583    user_roles user_roles_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (user_id);
 D   ALTER TABLE ONLY public.user_roles DROP CONSTRAINT user_roles_pkey;
       public         	   thokozani    false    223            �           2606    16585 "   user_roles user_roles_staff_id_key 
   CONSTRAINT     a   ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_staff_id_key UNIQUE (staff_id);
 L   ALTER TABLE ONLY public.user_roles DROP CONSTRAINT user_roles_staff_id_key;
       public         	   thokozani    false    223            �           2620    25880 1   library_resources notify_library_resources_delete    TRIGGER     �   CREATE TRIGGER notify_library_resources_delete AFTER DELETE ON public.library_resources FOR EACH ROW EXECUTE FUNCTION public.generate_admin_notification();
 J   DROP TRIGGER notify_library_resources_delete ON public.library_resources;
       public       	   thokozani    false    244    227            �           2620    25878 1   library_resources notify_library_resources_insert    TRIGGER     �   CREATE TRIGGER notify_library_resources_insert AFTER INSERT ON public.library_resources FOR EACH ROW EXECUTE FUNCTION public.generate_admin_notification();
 J   DROP TRIGGER notify_library_resources_insert ON public.library_resources;
       public       	   thokozani    false    244    227            �           2620    25879 1   library_resources notify_library_resources_update    TRIGGER     �   CREATE TRIGGER notify_library_resources_update AFTER UPDATE ON public.library_resources FOR EACH ROW EXECUTE FUNCTION public.generate_admin_notification();
 J   DROP TRIGGER notify_library_resources_update ON public.library_resources;
       public       	   thokozani    false    227    244            �           2620    25883    members notify_members_delete    TRIGGER     �   CREATE TRIGGER notify_members_delete AFTER DELETE ON public.members FOR EACH ROW EXECUTE FUNCTION public.generate_admin_notification();
 6   DROP TRIGGER notify_members_delete ON public.members;
       public       	   thokozani    false    221    244            �           2620    25881    members notify_members_insert    TRIGGER     �   CREATE TRIGGER notify_members_insert AFTER INSERT ON public.members FOR EACH ROW EXECUTE FUNCTION public.generate_admin_notification();
 6   DROP TRIGGER notify_members_insert ON public.members;
       public       	   thokozani    false    221    244            �           2620    25882    members notify_members_update    TRIGGER     �   CREATE TRIGGER notify_members_update AFTER UPDATE ON public.members FOR EACH ROW EXECUTE FUNCTION public.generate_admin_notification();
 6   DROP TRIGGER notify_members_update ON public.members;
       public       	   thokozani    false    221    244            �           2620    17313    staff notify_staff_delete    TRIGGER     �   CREATE TRIGGER notify_staff_delete AFTER DELETE ON public.staff FOR EACH ROW EXECUTE FUNCTION public.generate_admin_notification();
 2   DROP TRIGGER notify_staff_delete ON public.staff;
       public       	   thokozani    false    215    244            �           2620    17311    staff notify_staff_insert    TRIGGER     �   CREATE TRIGGER notify_staff_insert AFTER INSERT ON public.staff FOR EACH ROW EXECUTE FUNCTION public.generate_admin_notification();
 2   DROP TRIGGER notify_staff_insert ON public.staff;
       public       	   thokozani    false    215    244            �           2620    17312    staff notify_staff_update    TRIGGER     �   CREATE TRIGGER notify_staff_update AFTER UPDATE ON public.staff FOR EACH ROW EXECUTE FUNCTION public.generate_admin_notification();
 2   DROP TRIGGER notify_staff_update ON public.staff;
       public       	   thokozani    false    244    215            �           2606    17449 8   lending_transactions lending_transactions_member_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.lending_transactions
    ADD CONSTRAINT lending_transactions_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(member_id);
 b   ALTER TABLE ONLY public.lending_transactions DROP CONSTRAINT lending_transactions_member_id_fkey;
       public       	   thokozani    false    221    3278    231            �           2606    17454 :   lending_transactions lending_transactions_resource_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.lending_transactions
    ADD CONSTRAINT lending_transactions_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.library_resources(resource_id);
 d   ALTER TABLE ONLY public.lending_transactions DROP CONSTRAINT lending_transactions_resource_id_fkey;
       public       	   thokozani    false    227    231    3288            �           2606    17459 7   lending_transactions lending_transactions_staff_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.lending_transactions
    ADD CONSTRAINT lending_transactions_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(staff_id);
 a   ALTER TABLE ONLY public.lending_transactions DROP CONSTRAINT lending_transactions_staff_id_fkey;
       public       	   thokozani    false    3266    231    215            �           2606    16646 :   library_resources library_resources_added_by_staff_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.library_resources
    ADD CONSTRAINT library_resources_added_by_staff_id_fkey FOREIGN KEY (added_by_staff_id) REFERENCES public.staff(staff_id);
 d   ALTER TABLE ONLY public.library_resources DROP CONSTRAINT library_resources_added_by_staff_id_fkey;
       public       	   thokozani    false    215    3266    227            �           2606    16641 1   library_resources library_resources_genre_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.library_resources
    ADD CONSTRAINT library_resources_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES public.genres(genre_id);
 [   ALTER TABLE ONLY public.library_resources DROP CONSTRAINT library_resources_genre_id_fkey;
       public       	   thokozani    false    227    3270    217            �           2606    16787 *   notifications notifications_member_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(member_id) ON DELETE CASCADE;
 T   ALTER TABLE ONLY public.notifications DROP CONSTRAINT notifications_member_id_fkey;
       public       	   thokozani    false    221    3278    229            �           2606    16792 )   notifications notifications_staff_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(staff_id) ON DELETE CASCADE;
 S   ALTER TABLE ONLY public.notifications DROP CONSTRAINT notifications_staff_id_fkey;
       public       	   thokozani    false    229    3266    215            �           2606    16624 0   password_policies password_policies_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.password_policies
    ADD CONSTRAINT password_policies_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.user_roles(user_id);
 Z   ALTER TABLE ONLY public.password_policies DROP CONSTRAINT password_policies_user_id_fkey;
       public       	   thokozani    false    223    225    3280            �           2606    16586 #   user_roles user_roles_staff_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(staff_id);
 M   ALTER TABLE ONLY public.user_roles DROP CONSTRAINT user_roles_staff_id_fkey;
       public       	   thokozani    false    223    215    3266            �   8   x�3��K-/.H,H-�4�T���Q2�X%.#Τ��lNC�������D*F��� ϒ      �   )   x�3�t�L.����N�L�KNU��4��n��\1z\\\ ��      �   �   x��л�@��n�,����C0AJ�RD�?!(�Haɶ>�T�pad�G��$-�1��-�1���-�R�C��t)�|,�����`�ՠݒ&F��8��������)�-�˰dLsh�����
D������Z�A��9CP�I;4&��>O�Rg      �   �   x���K�  ��p
.І�~�K�'Х�X��1�no�^��K�	76-���
{��L	NDW�6�g�U(`�M�f���o�l�ȅ�����
�z1 "������wr��ݓ⣄5��?�>?j�6бc�{�z3�      �   {  x�}�Kk[AF�sE�ڌFҌ殒KK�І֔��l4�p��☀�}ǋ�nZ�>�$�A�L�OKg[g��g�ߘ�8��\O[ݟ��zmҥ�Ӟg7�;���|�%� z6�=K�V� Gp�+a�"F�i~���Ѽ����iD��2�bs~�f퇇/ww�}}�,��jk,�H�Q*�P�8l9� js [C1r.��JK�r��s"���~,ŖI���@�&�)t��؂��V��1��Ͽ�D�Ea���;��n��g=�m&���^����M��qIVѣ����׉�N�c��e�����I�i��M���*quPHA���ul�"V��(34����Ø�RO�V���	 x��	�֢>%�P�k놗�0� �}��      �   q   x���1�0F�9>���1"���'`�� $��ڽR������]h��[�2��6L�ZŹc�u�v���/��Χ$H��B��Rd�JV%��L?Ȍ�s��c�(J�'���.�      �      x������ � �         l   x�3�tL����,.)J,�/��CA`I�.#N�"���ĔDN���Ԝ��bNs���D ��\T�Y���W��ȩD �d`iiiaaajf "%���Ĵ4��1z\\\ �S%^      �   �   x�e��NAD��H���ڻNG�h�H!{�F ��|=���3O��	����p������%lҷ}�|{��Y�r<</wcԥR�'�i�^dX�e�qu֐��T8�,��(�u_0t����KZX-Q��œ��i!Ɇ%��8�?[������׃��v��O�J������������f	�"9��-�^}0�-D�@x�ѣ���`j��QI��l���M���5/���<�	c~     