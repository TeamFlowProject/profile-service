CREATE_QUERY = """
                CREATE (p:Profile {
                    id: $id,
                    mail: $mail,
                    password_hash: $password_hash,
                    registration_date: $registration_date,
                    name: $name,
                    surname: $surname,
                    patronymic: $patronymic,
                    stack: $stack,
                    skills: $skills,
                    experience: $experience,
                    desired_role: $desired_role,
                    busyness: $busyness,
                    contact_mail: $contact_mail,
                    contact_number: $contact_number,
                    work_place: $work_place,
                    work_position: $work_position,
                    city: $city,
                    portfolio: $portfolio,
                    about: $about,
                    status: $status
                })
                """

GET_PROFILE_QUERY = """
                MATCH (p:Profile {id: $id})
                RETURN collect(p) AS profile
                """

GET_PROFILES_QUERY = """
                UNWIND $ids AS id
                MATCH (p:Profile {id: id})
                return p
                """

UPDATE_PROFILE_QUERY = """
                MATCH (p:Profile {id: id})
                SET id = $id,
                    mail = $mail,
                    password_hash = $password_hash,
                    registration_date = $registration_date,
                    name = $name,
                    surname = $surname,
                    patronymic = $patronymic,
                    stack = $stack,
                    skills = $skills,
                    experience = $experience,
                    desired_role = $desired_role,
                    busyness = $busyness,
                    contact_mail = $contact_mail,
                    contact_number = $contact_number,
                    work_place = $work_place,
                    work_position = $work_position,
                    city = $city,
                    portfolio = $portfolio,
                    about = $about,
                    status = $status
                """
