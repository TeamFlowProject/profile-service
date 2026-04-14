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
                RETURN p
                """

GET_PROFILES_QUERY = """
                UNWIND $ids AS id
                MATCH (p:Profile {id: id})
                return p
                """

UPDATE_PROFILE_QUERY = """
                MATCH (p:Profile {id: $id})
                SET p.mail = $mail,
                    p.password_hash = $password_hash,
                    p.registration_date = $registration_date,
                    p.name = $name,
                    p.surname = $surname,
                    p.patronymic = $patronymic,
                    p.stack = $stack,
                    p.skills = $skills,
                    p.experience = $experience,
                    p.desired_role = $desired_role,
                    p.busyness = $busyness,
                    p.contact_mail = $contact_mail,
                    p.contact_number = $contact_number,
                    p.work_place = $work_place,
                    p.work_position = $work_position,
                    p.city = $city,
                    p.portfolio = $portfolio,
                    p.about = $about,
                    p.status = $status
                RETURN p
                """
