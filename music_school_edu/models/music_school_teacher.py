from odoo import models, fields

class MusicSchoolTeacher(models.Model):
    _name = "music.school.teacher"
    _description = "Music School Teacher"
    _inherits = {'res.partner':'partner_id'}

    # name = fields.Char(string="Name", required=True)
    # email = fields.Char(String="Email")
    # phone = fields.Char(String="Phone")

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Partner",
        help="Partner associated with this teacher",
        copy=False,
        ondelete='cascade',
    )
    reference = fields.Char(string="Reference")
    course_id = fields.One2many(
        comodel_name="music.school.course",
        inverse_name="teacher_id",
        string="Courses",
        help="Courses taught by the teacher"
    )

    lesson_id = fields.One2many(
        comodel_name="music.school.lesson",
        inverse_name="teacher_id",
        string="Lessons",
        help="Lessons conducted by the teacher"
    )
    level = fields.Selection(
        selection=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ],
        string="Level",
        default='beginner',
    )
    course_count = fields.Integer(
        string="Course Count",
        compute="_compute_course_count",
        help="Number of courses taught by the teacher"
    )
    def _compute_course_count(self):
        for record in self:
            record.course_count = self.env['music.school.course'].search_count([('teacher_id','=', record.id)])
    
    def action_view_courses(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Courses',
            'res_model': 'music.school.course',
            'view_mode': 'list,form',
            'domain': [('teacher_id', '=', self.id)],
            'context': {'default_teacher_id': self.id},
        }