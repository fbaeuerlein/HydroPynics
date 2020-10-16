module.exports = {
    adminAuth: {
        type: "credentials",
        users: [
            {
                username: "admin",
                password: "$2a$08$OiIpqZILm7AqNmz0/xDsju7H310DO3272PxbMfrsj55PQ8n1Ggrmy",
                permissions: "*"
            }
        ]
    },
    httpNodeAuth: { user: "admin", pass: "$2a$08$OiIpqZILm7AqNmz0/xDsju7H310DO3272PxbMfrsj55PQ8n1Ggrmy" },
    httpRoot: "/"
}
